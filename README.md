# Influencer-Engagement-and-Sponsorship-Coordination-Program
 
## Project Overview
This project is a comprehensive web application developed as part of the **Modern Application Development 1** course at IIT Madras. It focuses on managing influencer sponsorships and coordinating campaigns between influencers and sponsors.

## Features
### User Routes
- **Home Page**: Main landing page of the app (`GET /`)
- **Login**: User sign-in with email/password verification and two-factor authentication (`GET, POST /login`)
- **Logout**: Logs out the user and updates their status (`GET /logout`)
- **Profile Management**: View and edit user profiles, upload/remove profile pictures (`GET, POST /profile/<string:user>`)
- **Change Password**: Update passwords securely (`GET, POST /change-password/<string:user>`)
- **Delete Account**: Verify email before deleting accounts (`GET, POST /delete_account/<string:user>`)

### Help & Support
- **Help Requests**: Submit and track issues with a unique ID (`GET, POST /help`)
- **Forgot Password**: Recover passwords via OTP email verification (`GET, POST /forgot`)

### Admin Routes
- **Admin Dashboard**: Overview of campaigns and flagged content (`GET /admin/dashboard`)
- **Admin List**: Manage users, campaigns, and flagged items (`GET, POST /admin/list`)
- **Admin Actions**: Activate/deactivate or delete user accounts (`GET, POST /admin/<userId>/<action>`)
- **Admin Search**: Search for flagged items (`GET, POST /admin/search`)

### Influencer Routes
- **Dashboard**: View posts, campaigns, and profile details (`GET, POST /influencer_dashboard/<string:user_1>`)
- **Campaign Analysis**: Access influencer-specific campaign data (`GET /chart-data/influencer-campaigns/<sponsor_id>`)
- **Search Influencers**: Find influencers with filters (`GET /search/inf`)

### Sponsor Routes
- **Dashboard**: Manage campaigns and view analytics (`GET, POST /sponsor_dashboard/<string:user_1>`)
- **Add Campaign**: Create new campaigns with image uploads (`GET, POST /sponsor_dashboard/add_campaigns/<string:user>`)
- **Ads Analysis**: Visualize ad statuses (`GET /chart-data/ads/<sponsor_id>`)

### Reporting & Analysis
- **General Reports**: Display statistics for admin and user categories (`GET /info/<string:data>`)
- **Chart Data**: Generate visual analytics for various categories (`GET /chart-data/<category>/admin`)

### File Management
- **File Uploads**: Serve user-uploaded files (`GET /uploads/<filename>`)
- **Save File Function**: Save files securely on the server
- **Allowed File Types**: PNG, JPG, JPEG, GIF

### Security & Utility
- **OTP Verification**: Email-based OTP for secure operations
- **User Activity Tracking**: Track online/offline status
- **Password Hashing**: Secure storage and verification

## Technologies Used
- **Backend**: Python, Flask, Jinja2, Flask_SQLAlchemy, Flask_Login, Flask_Mail, UUID, Werkzeug
- **Frontend**: HTML, CSS, JavaScript, Bootstrap



