import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  define: {
    // Make environment variables available at build time with fallback values
    'process.env.REACT_APP_GROK_API_KEY': JSON.stringify(process.env.REACT_APP_GROK_API_KEY || 'gsk_...'),
    'process.env.REACT_APP_ASSEMBLY_AI_API_KEY': JSON.stringify(process.env.REACT_APP_ASSEMBLY_AI_API_KEY || 'React'),
    'process.env.REACT_APP_GROK_API_URL': JSON.stringify(process.env.REACT_APP_GROK_API_URL || 'https://api.groq.com/openai/v1'),
    'process.env.REACT_APP_ASSEMBLY_AI_API_URL': JSON.stringify(process.env.REACT_APP_ASSEMBLY_AI_API_URL || 'https://api.assemblyai.com/v2'),
  },
  optimizeDeps: {
    exclude: ['lucide-react'],
  },
});
