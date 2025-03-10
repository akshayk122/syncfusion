import React from 'react';
import './SyncfusionSlide.css';

/**
 * SyncfusionSlide - A React component that renders a PowerPoint slide
 * converted from Syncfusion JSON format.
 * 
 * The component preserves the visual properties of the PowerPoint elements including:
 * - Position (Left, Top, Width, Height)
 * - Formatting (Fill, LineFormat)
 * - Text content with formatting
 * - Rotation
 * - Shape types
 */
export const SyncfusionSlide = () => {
  return (
    <div 
      className="syncfusion-slide"
      style={{
        position: 'relative',
        width: '960px',
        height: '720px',
        backgroundColor: '#ffffff',
        overflow: 'hidden',
        boxSizing: 'border-box',
        fontFamily: 'Arial, sans-serif'
      }}
    >

    <div 
      id="shape_4"
      className="syncfusion-shape shape-rectangle"
      style={{ position: 'absolute',
        left: '65.62009841653543px',
        top: '49.822657595275594px',
        width: '158.2568222047244px',
        height: '51.699923243307076px',
        zIndex: 0,
        backgroundColor: '#f0f0f0' }}
      data-shape-type="Rectangle" data-slide-item-type="AutoShape"
    >
        <div style={{ textAlign: 'left' }}><span style={{ color: '#156082', fontFamily: 'Segoe UI, Roboto, Helvetica, Arial, sans-serif', fontSize: '26px' }}>Title here</span></div>
    </div>

    <div 
      id="shape_5"
      className="syncfusion-shape shape-rectangle"
      style={{ position: 'absolute',
        left: '64.60750252283464px',
        top: '158.1768224047244px',
        width: '81.31958672677165px',
        height: '32.3124651503937px',
        zIndex: 0,
        backgroundColor: '#f0f0f0' }}
      data-shape-type="Rectangle" data-slide-item-type="AutoShape"
    >
        <div style={{ textAlign: 'left' }}><span style={{ color: '#156082', fontFamily: 'Segoe UI, Roboto, Helvetica, Arial, sans-serif', fontSize: '14px' }}>Section</span></div>
    </div>

    <div 
      id="shape_7"
      className="syncfusion-shape shape-rectangle"
      style={{ position: 'absolute',
        left: '456.3027962480314px',
        top: '157.36674568976377px',
        width: '81.31958672677165px',
        height: '32.3124651503937px',
        zIndex: 0,
        backgroundColor: '#f0f0f0' }}
      data-shape-type="Rectangle" data-slide-item-type="AutoShape"
    >
        <div style={{ textAlign: 'left' }}><span style={{ color: '#156082', fontFamily: 'Segoe UI, Roboto, Helvetica, Arial, sans-serif', fontSize: '14px' }}>Section</span></div>
    </div>

    <div 
      id="shape_8"
      className="syncfusion-shape shape-rectangle bullet-indent"
      style={{ position: 'absolute',
        left: '65.2151650456693px',
        top: '241.4170342511811px',
        width: '164.45670171811022px',
        height: '145.40593569685038px',
        zIndex: 0,
        backgroundColor: '#f0f0f0' }}
      data-shape-type="Rectangle" data-slide-item-type="AutoShape" data-_bullet_indent_class="True"
    >
        <div style={{ textAlign: 'left' }}><span style={{ color: '#4EA72E', fontFamily: 'Segoe UI, Roboto, Helvetica, Arial, sans-serif', fontSize: '14px' }}>• Bullet points</span></div>
        <div style={{ textAlign: 'left', marginLeft: '20px' }}><span style={{ color: '#4EA72E', fontFamily: 'Segoe UI, Roboto, Helvetica, Arial, sans-serif', fontSize: '14px' }}>• Indent 1</span></div>
        <div style={{ textAlign: 'left', marginLeft: '20px' }}><span style={{ color: '#4EA72E', fontFamily: 'Segoe UI, Roboto, Helvetica, Arial, sans-serif', fontSize: '14px' }}>• Indent 2</span></div>
        <div style={{ textAlign: 'left' }}><span style={{ color: '#4EA72E', fontFamily: 'Segoe UI, Roboto, Helvetica, Arial, sans-serif', fontSize: '14px', fontWeight: 'bold' }}>• Bullet points</span></div>
        <div style={{ textAlign: 'left' }}><span style={{ color: '#156082', fontFamily: 'Segoe UI, Roboto, Helvetica, Arial, sans-serif', fontSize: '14px', fontStyle: 'italic' }}>• Bullet points</span></div>
    </div>

    <div 
      id="shape_2"
      className="syncfusion-shape shape-rectangle"
      style={{ position: 'absolute',
        left: '683.4268478590551px',
        top: '306.2849035771653px',
        width: '484.5702321409449px',
        height: '62.857060704724404px',
        zIndex: 0,
        backgroundColor: '#f0f0f0' }}
      data-shape-type="Rectangle" data-slide-item-type="AutoShape"
    >
        <div style={{ textAlign: 'center' }}><span style={{ color: '#FFFFFF', fontFamily: 'Segoe UI, Roboto, Helvetica, Arial, sans-serif', fontSize: '18px' }}>Header text</span></div>
    </div>

    <div 
      id="shape_3"
      className="syncfusion-shape shape-rightarrow"
      style={{ position: 'absolute',
        left: '297.1421442818897px',
        top: '511.99871999999993px',
        width: '158.85671571811022px',
        height: '60.57129214094488px',
        zIndex: 0,
        backgroundColor: '#f0f0f0' }}
      data-shape-type="RightArrow" data-slide-item-type="AutoShape"
    >
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', color: '#ffffff' }}>→</div>
    </div>
    </div>
  );
};

// CSS file (SyncfusionSlide.css) should include:
// .syncfusion-slide {
//   border: 1px solid #ccc;
//   box-shadow: 0 2px 5px rgba(0,0,0,0.1);
// }
// .syncfusion-shape {
//   box-sizing: border-box;
// }

export default SyncfusionSlide;
