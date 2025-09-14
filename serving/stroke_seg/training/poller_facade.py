"""Poller facade for managing the job polling lifecycle."""

import asyncio
import atexit
import threading
from typing import Optional

from stroke_seg.logging_config import get_logger
from stroke_seg.training.job_monitor import JobsMonitor


class PollerFacade:
    """
    Facade for managing the async job poller in a Flask application.
    
    Handles the lifecycle of the async polling service, including:
    - Starting the poller in a separate thread with event loop
    - Graceful shutdown on application exit
    - Health monitoring and status reporting
    """
    
    def __init__(self, jobs_monitor: Optional[JobsMonitor] = None):
        """
        Initialize poller facade.
        
        Args:
            jobs_monitor: JobPoller instance (creates new one if None)
        """
        self.logger = get_logger(__name__)
        self.jobs_monitor = jobs_monitor or JobsMonitor()
        
        self._thread: Optional[threading.Thread] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._shutdown_event = threading.Event()
        
        # Register shutdown handler
        atexit.register(self.shutdown)
        
        self.logger.info("PollerFacade initialized")
    
    def start(self) -> None:
        """Start the poller in a background thread."""
        if self._thread and self._thread.is_alive():
            self.logger.warning("Poller is already running")
            return
        
        self.logger.info("Starting poller facade")
        
        # Create and start background thread
        self._thread = threading.Thread(target=self._run_poller_thread, daemon=True)
        self._thread.start()
        
        self.logger.info("Poller facade started")
    
    def shutdown(self) -> None:
        """Shutdown the poller gracefully."""
        if not self._thread or not self._thread.is_alive():
            self.logger.debug("Poller is not running, nothing to shutdown")
            return
        
        self.logger.info("Shutting down poller facade")
        
        # Signal shutdown
        self._shutdown_event.set()
        
        # Stop the poller if we have access to the loop
        if self._loop and not self._loop.is_closed():
            try:
                # Schedule the stop coroutine in the event loop
                future = asyncio.run_coroutine_threadsafe(self.jobs_monitor.stop(), self._loop)
                future.result(timeout=10.0)  # Wait up to 10 seconds
            except Exception as e:
                self.logger.error(f"Error stopping job poller: {str(e)}", exc_info=True)
        
        # Wait for thread to finish
        if self._thread:
            self._thread.join(timeout=15.0)
            if self._thread.is_alive():
                self.logger.warning("Poller thread did not shutdown gracefully within timeout")
        
        self.logger.info("Poller facade shutdown complete")
    
    def _run_poller_thread(self) -> None:
        """Run the async poller in a dedicated thread."""
        try:
            self.logger.debug("Starting poller thread")
            
            # Create new event loop for this thread
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            
            # Run the async poller
            self._loop.run_until_complete(self._async_poller_main())
            
        except Exception as e:
            self.logger.error(f"Error in poller thread: {str(e)}", exc_info=True)
        finally:
            # Clean up event loop
            if self._loop:
                try:
                    self._loop.close()
                except Exception as e:
                    self.logger.error(f"Error closing event loop: {str(e)}")
            
            self.logger.debug("Poller thread ended")
    
    async def _async_poller_main(self) -> None:
        """Main async function for the poller."""
        try:
            self.logger.info("Starting job poller in async context")
            # Start the job poller
            await self.jobs_monitor.start()
            self.logger.info("Job poller started successfully")
            
            # Wait for shutdown signal
            while not self._shutdown_event.is_set():
                await asyncio.sleep(1.0)
                
                # Check if poller is still running
                if not self.jobs_monitor.is_running:
                    self.logger.warning("Job poller stopped unexpectedly - checking status")
                    poller_status = self.jobs_monitor.get_status()
                    self.logger.error(f"Poller status when stopped: {poller_status}")
                    break
            
            self.logger.info("Shutdown signal received, stopping job poller")
            
        except Exception as e:
            self.logger.error(f"Error in async poller main: {str(e)}", exc_info=True)
        finally:
            # Ensure poller is stopped
            try:
                await self.jobs_monitor.stop()
            except Exception as e:
                self.logger.error(f"Error stopping job poller in async context: {str(e)}", exc_info=True)
    
    @property
    def is_running(self) -> bool:
        """Check if poller facade is running."""
        return (
            self._thread is not None and 
            self._thread.is_alive() and 
            self.jobs_monitor.is_running
        )
    
    def get_status(self) -> dict:
        """Get comprehensive status of the poller facade."""
        return {
            'facade_running': self._thread is not None and self._thread.is_alive(),
            'thread_alive': self._thread.is_alive() if self._thread else False,
            'shutdown_requested': self._shutdown_event.is_set(),
            'poller_status': self.jobs_monitor.get_status(),
            'loop_running': self._loop is not None and not self._loop.is_closed() if self._loop else False
        }
    
    async def poll_job_once(self, job_id: str) -> Optional[dict]:
        """
        Poll a specific job once.
        
        Args:
            job_id: Internal job UUID
            
        Returns:
            Job status information or None if unavailable
        """
        if not self.is_running:
            self.logger.warning("Cannot poll job - poller is not running")
            return None
        
        try:
            # Run the poll in the poller's event loop
            if self._loop:
                future = asyncio.run_coroutine_threadsafe(
                    self.jobs_monitor.poll_job_once(job_id),
                    self._loop
                )
                return future.result(timeout=30.0)
            else:
                self.logger.error("No event loop available for polling")
                return None
        except Exception as e:
            self.logger.error(f"Error polling job {job_id}: {str(e)}")
            return None