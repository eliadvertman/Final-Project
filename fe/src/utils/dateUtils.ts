/**
 * Date utility functions for formatting ISO timestamp strings with microseconds
 * Strictly handles only the format: "2025-09-09T13:59:45.684945+00:00Z"
 * Returns "Invalid Date" for any other format
 */

// Regex pattern for exact ISO timestamp format with microseconds: YYYY-MM-DDTHH:MM:SS.ssssss+HH:MMZ
const ISO_TIMESTAMP_REGEX = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}[+-]\d{2}:\d{2}Z$/;

/**
 * Validates if a string matches the exact ISO timestamp format with microseconds
 * @param dateString - String to validate
 * @returns true if format matches exactly, false otherwise
 */
function isValidISOFormat(dateString: any): boolean {
  // Check if it's a string and matches the exact format
  return typeof dateString === 'string' && ISO_TIMESTAMP_REGEX.test(dateString);
}

/**
 * Formats a date string to a user-friendly format
 * Only accepts exact format: "2025-09-09T13:59:45.684945+00:00Z"
 * @param dateString - ISO timestamp string with microseconds
 * @returns Formatted date string or "Invalid Date" if format doesn't match
 */
export function formatDateTime(dateString: any): string {
  // Strict format validation - must match exact ISO format
  if (!isValidISOFormat(dateString)) {
    console.warn(`Invalid date format. Expected: YYYY-MM-DDTHH:MM:SS.ssssss+HH:MMZ, got: ${dateString}`);
    return 'Invalid Date';
  }

  try {
    // Remove the trailing 'Z' if present after timezone offset for JavaScript Date parsing
    // Convert format "2025-09-09T13:59:45.684945+00:00Z" -> "2025-09-09T13:59:45.684945+00:00"
    const parseableString = dateString.endsWith('Z') ? dateString.slice(0, -1) : dateString;
    const date = new Date(parseableString);
    
    // Double-check if the date is valid after parsing
    if (isNaN(date.getTime())) {
      console.warn(`Date parsing failed for valid format: ${dateString}`);
      return 'Invalid Date';
    }
    
    // Format with user's locale and timezone
    return date.toLocaleString(undefined, {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      timeZoneName: 'short'
    });
  } catch (error) {
    console.error(`Error formatting date: ${dateString}`, error);
    return 'Invalid Date';
  }
}

/**
 * Formats a date string to show date only
 * Only accepts exact format: "2025-09-09T13:59:45.684945+00:00Z"
 * @param dateString - ISO timestamp string with microseconds
 * @returns Formatted date string or "Invalid Date" if format doesn't match
 */
export function formatDate(dateString: any): string {
  // Strict format validation - must match exact ISO format
  if (!isValidISOFormat(dateString)) {
    console.warn(`Invalid date format. Expected: YYYY-MM-DDTHH:MM:SS.ssssss+HH:MMZ, got: ${dateString}`);
    return 'Invalid Date';
  }

  try {
    // Remove the trailing 'Z' if present after timezone offset for JavaScript Date parsing
    const parseableString = dateString.endsWith('Z') ? dateString.slice(0, -1) : dateString;
    const date = new Date(parseableString);
    
    if (isNaN(date.getTime())) {
      console.warn(`Date parsing failed for valid format: ${dateString}`);
      return 'Invalid Date';
    }
    
    return date.toLocaleDateString(undefined, {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    });
  } catch (error) {
    console.error(`Error formatting date: ${dateString}`, error);
    return 'Invalid Date';
  }
}

/**
 * Formats a date string to show time only
 * Only accepts exact format: "2025-09-09T13:59:45.684945+00:00Z"
 * @param dateString - ISO timestamp string with microseconds
 * @returns Formatted time string or "Invalid Date" if format doesn't match
 */
export function formatTime(dateString: any): string {
  // Strict format validation - must match exact ISO format
  if (!isValidISOFormat(dateString)) {
    console.warn(`Invalid date format. Expected: YYYY-MM-DDTHH:MM:SS.ssssss+HH:MMZ, got: ${dateString}`);
    return 'Invalid Date';
  }

  try {
    // Remove the trailing 'Z' if present after timezone offset for JavaScript Date parsing
    const parseableString = dateString.endsWith('Z') ? dateString.slice(0, -1) : dateString;
    const date = new Date(parseableString);
    
    if (isNaN(date.getTime())) {
      console.warn(`Date parsing failed for valid format: ${dateString}`);
      return 'Invalid Date';
    }
    
    return date.toLocaleTimeString(undefined, {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  } catch (error) {
    console.error(`Error formatting time: ${dateString}`, error);
    return 'Invalid Date';
  }
}

/**
 * Formats a date string to show relative time (e.g., "2 hours ago")
 * Only accepts exact format: "2025-09-09T13:59:45.684945+00:00Z"
 * @param dateString - ISO timestamp string with microseconds
 * @returns Relative time string or "Invalid Date" if format doesn't match
 */
export function formatRelativeTime(dateString: any): string {
  // Strict format validation - must match exact ISO format
  if (!isValidISOFormat(dateString)) {
    console.warn(`Invalid date format. Expected: YYYY-MM-DDTHH:MM:SS.ssssss+HH:MMZ, got: ${dateString}`);
    return 'Invalid Date';
  }

  try {
    // Remove the trailing 'Z' if present after timezone offset for JavaScript Date parsing
    const parseableString = dateString.endsWith('Z') ? dateString.slice(0, -1) : dateString;
    const date = new Date(parseableString);
    
    if (isNaN(date.getTime())) {
      console.warn(`Date parsing failed for valid format: ${dateString}`);
      return 'Invalid Date';
    }
    
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMinutes = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    
    if (diffMinutes < 1) {
      return 'Just now';
    } else if (diffMinutes < 60) {
      return `${diffMinutes} minute${diffMinutes === 1 ? '' : 's'} ago`;
    } else if (diffHours < 24) {
      return `${diffHours} hour${diffHours === 1 ? '' : 's'} ago`;
    } else if (diffDays < 7) {
      return `${diffDays} day${diffDays === 1 ? '' : 's'} ago`;
    } else {
      // For dates older than 7 days, show the actual date
      return formatDateTime(dateString);
    }
  } catch (error) {
    console.error(`Error formatting relative time: ${dateString}`, error);
    return 'Invalid Date';
  }
}

/**
 * Default export - the main formatting function for created_at fields
 */
export default formatDateTime;