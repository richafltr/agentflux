Sure, here is a simplified example of how you might implement this A/B testing variation using React, TypeScript, and Tailwind CSS. This example includes a hero section, a content section, and a footer section. Each section is a separate component. 

```jsx
import React from 'react';
import './App.css';

// Conversion tracking hook
const useConversionTracking = () => {
  // Implement your conversion tracking logic here
};

// A/B testing metadata
const ABTestingMetadata = {
  variant: 'hero_dominant',
  pattern: 'Hero-First Layout',
};

// Hero section
const HeroSection: React.FC = () => {
  useConversionTracking();

  return (
    <section className="hero-section">
      <h1 className="text-4xl font-bold">Large, bold hero text</h1>
      <button className="btn-primary">Single primary CTA button</button>
    </section>
  );
};

// Content section
const ContentSection: React.FC = () => {
  return (
    <section className="content-section">
      <h2 className="text-2xl">Customer testimonials</h2>
      <div className="grid grid-cols-3 gap-4">
        {/* Implement your grid layout for social proof here */}
      </div>
    </section>
  );
};

// Footer section
const FooterSection: React.FC = () => {
  return (
    <footer className="footer-section">
      <h3 className="text-xl">Footer text</h3>
      <nav>
        {/* Implement your footer navigation here */}
      </nav>
    </footer>
  );
};

// Main component
const App: React.FC = () => {
  return (
    <div className="App">
      <HeroSection />
      <ContentSection />
      <FooterSection />
    </div>
  );
};

export default App;
```

This is a simplified example and doesn't include all the details from your A/B testing variation. You would need to expand this example to include all the components and styles specified in your variation. You would also need to implement the `useConversionTracking` hook to track conversions.

Please note that this example assumes you have a setup that supports TypeScript and Tailwind CSS. If you don't, you would need to set that up first.