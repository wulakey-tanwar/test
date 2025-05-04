import { createContext, useContext, useEffect, useState } from 'react';
const ThemeContext = createContext();
export const ThemeProvider = ({ children }) => {
    const [theme, setTheme] = useState('light');

    useEffect(() => {
        document.documentElement.classList.toggle('dark', theme === 'dark');
    }, [theme]);

    const toggleTheme = () => setTheme((prev) => (prev === 'light' ? 'dark' : 'light'));
    return <ThemeContext.Provider value={{ theme, toggleTheme }}>{children}</ThemeContext.Provider>;
};
export const useTheme = () => useContext(ThemeContext);
        