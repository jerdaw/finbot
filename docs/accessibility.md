# Accessibility Statement

**Last Updated:** 2026-02-17
**Compliance Level:** WCAG 2.1 Level AA (Partial Conformance)

## Overview

Finbot is committed to making the dashboard accessible to all users, including those with disabilities. This document describes our accessibility features, known limitations, and how to report accessibility issues.

## Accessibility Features

### Visual Accessibility

#### Color Contrast
- **Text Contrast:** All text meets WCAG 2.1 Level AA requirements (4.5:1 contrast ratio for normal text, 3:1 for large text)
- **UI Component Contrast:** Interactive elements meet 3:1 contrast ratio
- **High Contrast Mode:** Charts use black text on white backgrounds

#### Colorblind-Friendly Design
All charts use colorblind-friendly color palettes:
- **Primary Colors:** Blue (#0072B2), Orange (#D55E00), Green (#009E73)
- **Secondary Colors:** Purple (#CC79A7), Yellow (#F0E442), Sky Blue (#56B4E9)
- **Pattern Support:** Charts use line styles (solid, dashed) in addition to color
- **No Red/Green Combinations:** Avoid problematic color pairs for deuteranopia/protanopia

#### Chart Accessibility
- **Descriptive Titles:** All charts have clear, descriptive titles
- **Axis Labels:** X and Y axes are clearly labeled
- **Hover Information:** Detailed tooltips provide exact values on hover
- **Legend Contrast:** Legends have high-contrast backgrounds and borders
- **Large Font Sizes:** Chart text is at least 12pt

### Keyboard Navigation

#### Streamlit Framework Support
- **Tab Navigation:** Navigate between interactive elements using Tab/Shift+Tab
- **Enter/Space Activation:** Activate buttons and controls with Enter or Space
- **Arrow Key Navigation:** Navigate dropdowns and select boxes with arrow keys
- **Escape Key:** Close dropdowns and modals with Escape

#### Page Navigation
- **Sidebar Navigation:** Use Tab to access sidebar navigation links
- **Page Links:** All pages accessible via keyboard from home page
- **Focus Indicators:** Visible focus outlines on interactive elements (Streamlit default)

### Screen Reader Support

#### Semantic Structure
- **Page Titles:** Each page has a descriptive title (e.g., "Simulations — Finbot")
- **Headings:** Logical heading hierarchy (H1, H2, H3)
- **Labels:** Form inputs have associated labels
- **Alt Text:** Charts include descriptions for screen readers (via Plotly)

#### ARIA Support (Limited)
Due to Streamlit framework constraints, explicit ARIA attributes are limited. However:
- Chart descriptions added via Plotly layout
- Streamlit generates semantic HTML where possible
- Standard HTML form labels used

### Input Accessibility

#### Form Controls
- **Clear Labels:** All input fields have descriptive labels
- **Error Messages:** Validation errors are clearly displayed
- **Help Text:** Additional guidance provided where needed
- **Logical Tab Order:** Form fields follow logical reading order

#### Interactive Elements
- **Button Labels:** All buttons have descriptive text
- **Checkbox Labels:** Associated labels for all checkboxes
- **Dropdown Descriptions:** Select boxes have clear options
- **Date Pickers:** Accessible date selection interface (Streamlit default)

## Known Limitations

### Streamlit Framework Constraints

#### Limited ARIA Control
- **HTML Structure:** Cannot fully customize generated HTML
- **ARIA Attributes:** Limited ability to add custom ARIA labels/landmarks
- **Focus Management:** Cannot programmatically control focus
- **Skip Links:** Cannot add skip-to-content links

#### Component Limitations
- **Custom Components:** Some third-party components may not be fully accessible
- **Plotly Charts:** Interactive chart features may have limited screen reader support
- **Data Tables:** Large tables may be difficult to navigate with screen readers

#### Mobile Accessibility
- **Touch Targets:** Some controls may be small on mobile devices
- **Zoom Support:** Dashboard supports browser zoom, but layout may break at high zoom levels
- **Responsive Design:** Streamlit's responsive design has some limitations

### Planned Improvements

We are actively working to improve accessibility:
- [ ] Add more descriptive ARIA labels where Streamlit permits
- [ ] Improve mobile touch target sizes
- [ ] Add keyboard shortcuts documentation
- [ ] Conduct formal accessibility audit
- [ ] Test with multiple screen readers (NVDA, JAWS, VoiceOver)

## Assistive Technology Compatibility

### Tested With
- **Screen Readers:** Basic testing with browser screen readers
- **Keyboard Only:** Full keyboard navigation tested
- **Browser Zoom:** Tested at 100%-200% zoom

### Recommended Technologies
- **Screen Readers:** NVDA (Windows), JAWS (Windows), VoiceOver (macOS/iOS)
- **Browsers:** Chrome, Firefox, Safari, Edge (latest versions)
- **Zoom:** Browser native zoom (Ctrl/Cmd +)

## Accessibility Standards Compliance

### WCAG 2.1 Level AA Conformance

#### Perceivable (Partial Conformance)
- ✅ **1.1.1 Non-text Content (A):** Charts have descriptive titles and labels
- ✅ **1.4.3 Contrast (AA):** Text contrast meets 4.5:1 ratio
- ✅ **1.4.11 Non-text Contrast (AA):** UI components meet 3:1 ratio
- ⚠️ **1.4.4 Resize Text (AA):** Partial - some layout issues at 200% zoom
- ⚠️ **1.4.13 Content on Hover/Focus (AA):** Limited control over Streamlit tooltips

#### Operable (Partial Conformance)
- ✅ **2.1.1 Keyboard (A):** All functionality available via keyboard
- ✅ **2.4.2 Page Titled (A):** All pages have descriptive titles
- ✅ **2.4.7 Focus Visible (AA):** Keyboard focus is visible
- ⚠️ **2.4.1 Bypass Blocks (A):** No skip links (Streamlit limitation)
- ⚠️ **2.4.3 Focus Order (A):** Generally logical, but some Streamlit quirks

#### Understandable (Partial Conformance)
- ✅ **3.1.1 Language of Page (A):** Page language set to English
- ✅ **3.2.1 On Focus (A):** No unexpected context changes
- ✅ **3.3.2 Labels or Instructions (A):** Form inputs have labels
- ⚠️ **3.3.1 Error Identification (A):** Limited error messaging (Streamlit default)

#### Robust (Partial Conformance)
- ⚠️ **4.1.2 Name, Role, Value (A):** Relies on Streamlit-generated HTML
- ⚠️ **4.1.3 Status Messages (AA):** Limited ARIA live region support

### Section 508 Compliance
The dashboard aims for Section 508 compliance where technically feasible within Streamlit constraints.

### EN 301 549 (European Standard)
Aligned with EN 301 549 accessibility requirements for web content.

## How to Use the Dashboard Accessibly

### Keyboard Shortcuts
- **Tab:** Move forward between elements
- **Shift+Tab:** Move backward between elements
- **Enter/Space:** Activate buttons and controls
- **Arrow Keys:** Navigate dropdowns
- **Escape:** Close dropdowns/modals

### Screen Reader Tips
1. **Navigate by Headings:** Use heading navigation (H key in most screen readers)
2. **Chart Information:** Navigate to chart title to hear description
3. **Forms:** Use form navigation mode for input fields
4. **Tables:** Use table navigation mode for data tables

### Zoom and Magnification
1. **Browser Zoom:** Ctrl/Cmd + or Ctrl/Cmd - (recommended: up to 150%)
2. **Text Only Zoom:** Use browser's text-only zoom for better layout preservation
3. **Operating System Magnifier:** Windows Magnifier or macOS Zoom work well

## Reporting Accessibility Issues

We welcome feedback on accessibility issues and barriers.

### How to Report
- **GitHub Issues:** [https://github.com/jerdaw/finbot/issues](https://github.com/jerdaw/finbot/issues)
- **Email:** Create an issue on GitHub or include accessibility concerns in bug reports
- **Include:**
  - Page/feature affected
  - Assistive technology used (screen reader, keyboard, etc.)
  - Browser and version
  - Description of the issue
  - Expected behavior

### Response Time
We aim to respond to accessibility issues within:
- **Critical Issues:** 1-2 business days
- **High Priority:** 1 week
- **Medium/Low Priority:** 2-4 weeks

### Priority Levels
- **Critical:** Core functionality inaccessible, blocking all users of assistive tech
- **High:** Major feature inaccessible, significant user impact
- **Medium:** Feature partially accessible, workarounds available
- **Low:** Minor inconvenience, minimal user impact

## Third-Party Content

### Streamlit Framework
The dashboard is built with Streamlit, which has its own accessibility considerations:
- [Streamlit Accessibility](https://docs.streamlit.io/)
- Some limitations are inherent to the framework

### Plotly Charts
Charts are created with Plotly, which provides some accessibility features:
- [Plotly Accessibility](https://plotly.com/python/accessibility/)
- Interactive features may have limited screen reader support

### Dependencies
We use third-party libraries that may have their own accessibility constraints. We work to mitigate these where possible.

## Accessibility Roadmap

### Short Term (1-3 months)
- [ ] Conduct formal WCAG 2.1 audit with accessibility testing tools
- [ ] Test with NVDA, JAWS, and VoiceOver screen readers
- [ ] Document keyboard shortcuts comprehensively
- [ ] Improve mobile touch target sizes

### Medium Term (3-6 months)
- [ ] Add more ARIA landmarks where Streamlit permits
- [ ] Create accessibility testing checklist for new features
- [ ] Add automated accessibility testing to CI/CD
- [ ] User testing with people with disabilities

### Long Term (6-12 months)
- [ ] Explore alternative frameworks with better accessibility support
- [ ] Create accessible data export features (CSV/Excel)
- [ ] Add audio descriptions for complex charts
- [ ] Implement user preference settings (high contrast mode, reduced motion)

## References

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [WebAIM Resources](https://webaim.org/resources/)
- [Section 508 Standards](https://www.section508.gov/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Plotly Accessibility](https://plotly.com/python/accessibility/)

## Legal

This accessibility statement is provided in good faith and represents our ongoing commitment to accessibility. While we strive for full compliance with WCAG 2.1 Level AA, some limitations are inherent to the Streamlit framework. We continue to work toward improving accessibility where technically feasible.

**Finbot is not a commercial product and is provided "as is" without warranty.** Accessibility improvements are made on a best-effort basis within the constraints of the underlying framework.

---

**Questions or concerns?** Please file an issue on our [GitHub repository](https://github.com/jerdaw/finbot/issues).
