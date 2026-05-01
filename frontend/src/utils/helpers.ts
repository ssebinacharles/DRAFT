// If you exported the User interface from your AuthContext, 
// you can import it here. Otherwise, we define a lightweight version for the helpers.
interface MinimalUser {
  role?: string;
  [key: string]: any;
}

/**
 * Returns true if the user has the specified role.
 */
export const hasRole = (user: MinimalUser | null | undefined, role: string): boolean => {
  return user?.role === role;
};

/**
 * Convenience helpers to check specific roles.
 */
export const isStudent = (user: MinimalUser | null | undefined): boolean => hasRole(user, "STUDENT");
export const isSupervisor = (user: MinimalUser | null | undefined): boolean => hasRole(user, "SUPERVISOR");
export const isAdministrator = (user: MinimalUser | null | undefined): boolean => hasRole(user, "ADMINISTRATOR");

/**
 * Formats a date into a locale-specific string.
 */
export const formatDate = (
  date: string | number | Date, 
  locale: string = "en-US", 
  options?: Intl.DateTimeFormatOptions
): string => {
  if (!date) return "N/A";
  return new Date(date).toLocaleDateString(locale, options);
};

/**
 * Performs a shallow equality check between two objects.
 */
export const shallowEqual = <T extends Record<string, any>>(obj1: T, obj2: T): boolean => {
  if (obj1 === obj2) return true;
  if (!obj1 || !obj2) return false;
  
  const keys1 = Object.keys(obj1);
  const keys2 = Object.keys(obj2);
  
  if (keys1.length !== keys2.length) return false;
  
  for (const key of keys1) {
    if (obj1[key] !== obj2[key]) return false;
  }
  return true;
};

/**
 * Deep clones an object using JSON serialization.
 * Note: This will strip out functions and undefined values.
 */
export const deepClone = <T>(value: T): T => {
  if (value === undefined) return value;
  return JSON.parse(JSON.stringify(value));
};