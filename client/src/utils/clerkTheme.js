/**
 * Clerk Theme Configuration
 * Using Clerk's official dark theme with minimal customization
 */
import { dark } from '@clerk/themes';

export const clerkAppearance = {
    baseTheme: dark,
    variables: {
        colorPrimary: '#3b82f6',
        fontFamily: 'Inter, system-ui, sans-serif',
    },
    localization: {
        signIn: {
            start: {
                title: 'Sign-in to Express AI',
                subtitle: 'Welcome back! Please sign in to continue',
            },
        },
        signUp: {
            start: {
                title: 'Sign-up for Express AI',
                subtitle: 'Create an account to get started',
            },
        },
    },
};

export default clerkAppearance;
