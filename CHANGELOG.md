# Changelog

All notable changes to TerraformingMarsWebServer are documented in this file.

## [3.0.0] - 2025-12-07 (Season 3 Release - Jupiter Theme)

### Major Features
- ✅ **Jupiter Season Theme**: Full Season 3 support with dynamic blue/purple styling and Jupiter imagery
- ✅ **Enhanced Drag-and-Drop**: Desktop drag-and-drop + mobile touch support (500ms long-press)
- ✅ **Click-to-Place Alternative**: Support for both drag-drop and click-based player placement
- ✅ **Extended Player Support**: Increased from 5 to 6 players per game session
- ✅ **Awards & Milestones**: Full tracking with numbered labels and winner assignments
- ✅ **CSV Map Tracking**: Persistent "Spin the Map" history excludes last-played options
- ✅ **Role-Based Access Control**: Admin and user roles with specific permissions
- ✅ **Fearless Draft Admin**: Special feature for managing corporation pool count
- ✅ **Mobile Optimization**: Numeric keypad on game score inputs, touch-friendly UI

### UI/UX Improvements
- ✅ Form alignment with auto-width labels and consistent content widths
- ✅ Season-themed color variables throughout CSS
- ✅ Numbered milestone/award labels (1st, 2nd, 3rd, etc.)
- ✅ Stacked awards layout (1st place above 2nd place)
- ✅ Fixed sidebar (180px) for constant player pool access
- ✅ Click-to-deselect placed players (no removal button needed)
- ✅ Visual player states: available → selected → placed → grayed
- ✅ Responsive design tested on desktop, tablet, and mobile

### Technical Improvements
- ✅ Modular JavaScript with clear drag-drop logic
- ✅ Simplified placement system (sidebar → empty slot only)
- ✅ CSV-based map history with proper encoding handling
- ✅ UTF-8 file support for international characters (Danish characters)
- ✅ Proper CSV parsing with python csv module
- ✅ Flask API endpoints for map tracking
- ✅ Enhanced error handling and debugging

### Backend Updates
- ✅ Map tracking API endpoints: `/api/get_last_map`, `/api/update_map_history`
- ✅ CSV file handling with header management
- ✅ Player credentials from UTF-8 encoded text file
- ✅ Session-based authentication
- ✅ Fearless draft settings management

### Bug Fixes
- ✅ Fixed player disappearing when clicked in ranking slots
- ✅ Prevented duplicate players in same ranking slot
- ✅ Fixed UTF-8 encoding for special characters in credentials
- ✅ Corrected click handler logic (inverted condition)
- ✅ Fixed map filtering to exclude last-played maps

### Code Quality
- ✅ Added comprehensive docstrings to all functions
- ✅ Organized code sections with clear headers
- ✅ Updated .gitignore with Python/IDE standards
- ✅ Expanded README with detailed documentation
- ✅ Added API endpoint documentation
- ✅ Improved error messages and console logging

### Documentation
- ✅ Comprehensive README with feature list and setup instructions
- ✅ API endpoint reference documentation
- ✅ Project structure documentation
- ✅ Installation and usage guide
- ✅ Configuration examples

### Known Limitations
- Single instance deployment (no concurrent sessions)
- In-memory session management (resets on server restart)
- Results stored in JSON (consider database for large datasets)

### Migration from Season 2
- Existing results.json remains compatible (season defaults to 1)
- Player credentials need to be formatted in PLAYER_CREDENTIALS.txt
- User settings imported from user_settings.json if exists

---

## [2.x.x] - Previous Releases (Season 1 & 2)

### Features (Season 1 & 2)
- ✅ Basic game result logging
- ✅ Player ranking system
- ✅ Seasonal tracking
- ✅ Statistics and charts
- ✅ Hall of Fame
- ✅ Responsive design

---

## Future Roadmap

### Planned Features
- [ ] Database integration (PostgreSQL/SQLite)
- [ ] Multi-device sync
- [ ] Game replay analysis
- [ ] Advanced statistics (win rate, average score trends)
- [ ] Custom season creation
- [ ] Photo uploads for game sessions
- [ ] Multiplayer real-time updates
- [ ] Mobile app (React Native/Flutter)
- [ ] Dark mode toggle
- [ ] Export to PDF/Excel

### Performance Improvements
- [ ] Caching layer (Redis)
- [ ] Asynchronous task queue (Celery)
- [ ] Database indexing
- [ ] API rate limiting

### Security Enhancements
- [ ] CSRF protection
- [ ] Rate limiting
- [ ] Input validation
- [ ] Two-factor authentication
- [ ] Audit logging

---

## Contributing

To contribute to this project, please:
1. Create a feature branch from `main`
2. Make your changes with clear commit messages
3. Test on desktop and mobile
4. Submit a pull request with detailed description

## License

Specify your license here.

## Support

For issues or questions, please open an issue on GitHub.
