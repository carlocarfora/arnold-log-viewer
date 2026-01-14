# Arnold Log Viewer - TODO List

## 🐛 Fix Immediately (Critical Bugs)

- [x] **Bug #1**: Error display loop - Fixed error iteration to display individual errors
- [x] **Bug #3**: Inconsistent warning parsing - Made warning parsing consistent with error parsing
- [ ] **Bug #2**: Hardcoded memory values - Replace hardcoded strings with parsed data
- [ ] **Bug #4**: Missing file error handling - Add try-except for example_log.log
- [ ] **Bug #5**: Wrong return type annotation - Fix get_render_time() type hint
- [ ] **Bug #6**: Unused imports - Clean up unused imports
- [ ] **Bug #7**: Unused variables - Remove unused variables

## 🔧 High Priority (Core Improvements)

- [ ] **Core #1**: Parser efficiency - Compile regex patterns once as class attributes
- [ ] **Core #6**: Error handling strategy - Add try-except blocks around critical operations
- [ ] **Core #10**: Display camera/GPU info - Show parsed camera and GPU data in UI

## 📊 Medium Priority

- [ ] **Core #8**: Regex compilation optimization
- [ ] **Core #5**: Session state management improvements
- [ ] **Core #2**: Display all parsed fields in UI
- [ ] **Core #3**: Data validation for parsed values
- [ ] **Core #4**: Empty data handling improvements

## ✨ Polish (Nice-to-Have)

- [ ] **Polish #1**: Loading states with spinners
- [ ] **Polish #3**: Chart improvements (tooltips, colors, downloadable)
- [ ] **Polish #7**: Time formatting consistency
- [ ] **Polish #8**: Units consistency (MB vs GB)
- [ ] **Polish #2**: Color coding for thresholds
- [ ] **Polish #9**: Performance metrics dashboard
- [ ] **Polish #5**: Log comparison mode
- [ ] **Polish #11**: Historical tracking
- [ ] **Polish #12**: Smart optimization suggestions

## 🚀 Future Enhancements

- [ ] Batch processing for multiple logs
- [ ] Permalink/sharing functionality
- [ ] Arnold version detection and warnings
- [ ] Search and filter capabilities
- [ ] Mobile responsive improvements

---

Last updated: 2026-01-15
