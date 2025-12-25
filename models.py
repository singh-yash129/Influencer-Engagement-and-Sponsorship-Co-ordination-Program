from config import *
class AdminFlag(db.Model):
    __tablename__ = 'admin_flag'
    user_id = db.Column(db.String, primary_key=True)
    campaign_id =db.Column(db.String)
    flag = db.Column(db.String)
    role = db.Column(db.String)
class Flag(db.Model):
    __tablename__ = 'flags'
    flag_id = db.Column(db.String, primary_key=True, unique=True)
    flagged_user_id = db.Column(db.String, db.ForeignKey('user.username'), nullable=False)
    flagger_user_id = db.Column(db.String, db.ForeignKey('user.username'), nullable=False)
    reason = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    flagged_user = db.relationship('User', foreign_keys=[flagged_user_id])
    flagger_user = db.relationship('User', foreign_keys=[flagger_user_id])
class Help(db.Model):
    __tablename__='help'
    email=db.Column(db.String(80), nullable=False, primary_key=True)
    Name=db.Column(db.String(80),  nullable=False)
    problem=db.Column(db.String(800), nullable=False)
    subject=db.Column(db.String(100),nullable=False)
    status=db.Column(db.String(80), nullable=False)
    issue_id=db.Column(db.String(100),nullable=False,unique=True)

class Campaign(db.Model):
    __tablename__ = "campaign"
    campaign_id = db.Column(db.String, primary_key=True, nullable=False, unique=True)
    user_id = db.Column(db.String, db.ForeignKey('user.username'), nullable=False)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    niche = db.Column(db.String, nullable=False)
    start = db.Column(db.Date, nullable=False)
    end = db.Column(db.Date, nullable=False)
    target = db.Column(db.String, nullable=False)
    budget = db.Column(db.Integer, nullable=False)
    goal = db.Column(db.Integer, nullable=False)
    currency = db.Column(db.String, nullable=False)
    image = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False)
    privacy=db.Column(db.String, nullable=False)

    user = db.relationship("User", back_populates="campaigns")
    adds = db.relationship("Add", back_populates="campaign", cascade="all, delete-orphan")

class Add(db.Model):
    __tablename__ = "add"
    campaign_id = db.Column(db.String, db.ForeignKey('campaign.campaign_id'), primary_key=True)
    influencer_id = db.Column(db.String, db.ForeignKey('user.username'), primary_key=True)
    sponsor_id=db.Column(db.String, db.ForeignKey('user.username'), primary_key=True)
    messages = db.Column(db.String)
    requirements = db.Column(db.String)
    payment_amount = db.Column(db.Integer)
    status = db.Column(db.String, nullable=False)
    flagged = db.Column(db.String, default=False)
    revised_payment = db.Column(db.Integer, nullable=True)
    request_id=db.Column(db.String,nullable=False,unique=True)  # New column for revised payment during negotiation


    campaign = db.relationship("Campaign", back_populates="adds")
    influencer = db.relationship("User", foreign_keys=[influencer_id])
class Payments(db.Model):
    __tablename__ = 'payment'
    user_id = db.Column(db.String(80), nullable=False, primary_key=True)
    transaction_id = db.Column(db.String(80), nullable=False, primary_key=True)
    campaign_id = db.Column(db.String(80), nullable=False, primary_key=True)
    status = db.Column(db.String(80), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    sponsor = db.Column(db.String(80), nullable=False)  # New column for sponsor ID


class History(db.Model):
    __tablename__="history"
    user_id=db.Column(db.String(80), unique=True, nullable=False, primary_key=True)
    role=db.Column(db.String(80), nullable=False)
    campaign_run=db.Column(db.String(80), nullable=False)
    campaign_success=db.Column(db.String(80), nullable=False)
    campaign_expired=db.Column(db.String(80),nullable=False)
    add_run=db.Column(db.String(80),nullable=False)
    flags=db.Column(db.String(80), nullable=False)
    createdAt=db.Column(db.String,default=datetime.utcnow)

class Post(db.Model):
    __tablename__ = "posts"
    post_id = db.Column(db.String, unique=True, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('user.username'), nullable=False)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.Text, nullable=False)
    media_type = db.Column(db.String(50), nullable=True)
    media_url = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    def get_id(self):
        return self.post_id

class Event(db.Model):
    __tablename__ = "events"
    event_id = db.Column(db.String, unique=True, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('user.username'), nullable=False)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    date = db.Column(db.Text, nullable=False)
    start_time = db.Column(db.Text, nullable=False)
    end_time = db.Column(db.Text, nullable=False)
    media = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    def get_id(self):
        return self.event_id

class Announce(db.Model):
    __tablename__ = "announces"
    announce_id = db.Column(db.String, unique=True, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('user.username'), nullable=False)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    def get_id(self):
        return self.announce_id
class Comment(db.Model):
    __tablename__ = "comments"
    comment_id = db.Column(db.Integer, primary_key=True)
    content_type = db.Column(db.String, nullable=False)
    content_id = db.Column(db.String, nullable=False)
    user_id = db.Column(db.String, db.ForeignKey('user.username'), nullable=False)
    content = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship('User', back_populates='comments')

class Like(db.Model):
    __tablename__ = "likes"
    like_id = db.Column(db.Integer, primary_key=True)
    content_type = db.Column(db.String, nullable=False)
    content_id = db.Column(db.String, nullable=False)
    user_id = db.Column(db.String, db.ForeignKey('user.username'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship('User', back_populates='likes')
class Friendship(db.Model):
    __tablename__ = "friendships"
    friendship_id = db.Column(db.Integer, primary_key=True)
    user_id1 = db.Column(db.String, db.ForeignKey('user.username'), nullable=False)
    user_id2 = db.Column(db.String, db.ForeignKey('user.username'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
class FriendRequest(db.Model):
    __tablename__ = "friend_requests"
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.String, db.ForeignKey('user.username'), nullable=False)
    receiver_id = db.Column(db.String, db.ForeignKey('user.username'), nullable=False)
    status = db.Column(db.String, nullable=False, default='pending')  # 'pending', 'accepted', 'rejected', 'flagged'

    sender = db.relationship("User", foreign_keys=[sender_id])
    receiver = db.relationship("User", foreign_keys=[receiver_id])

class Notification(db.Model):
    __tablename__ = "notifications"
    notification_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('user.username'), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
class Follower(db.Model):
    __tablename__ = "followers"
    follower_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('user.username'), nullable=False)
    follower_user_id = db.Column(db.String, db.ForeignKey('user.username'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    two_factor_enabled = db.Column(db.String(80), default='False')
    username = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)
    email_id = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(64), nullable=False, default='ABC')
    last_name = db.Column(db.String(80), nullable=False, default='DEF')
    gender = db.Column(db.String(10), nullable=False, default='False')
    dob = db.Column(db.String, nullable=False, default='False')
    role = db.Column(db.String(100), default='sponsor', nullable=False)
    platform_youtube = db.Column(db.String, default='False')
    platform_linkedin = db.Column(db.String, default='False')
    platform_instagram = db.Column(db.String, default='False')
    platform_facebook = db.Column(db.String, default='False')
    platform_twitter = db.Column(db.String, default='False')
    profile_picture = db.Column(db.String(250))
    industry = db.Column(db.String(10), default='XYZ')
    activity = db.Column(db.String(20), nullable=False, default='offline')
    passcode = db.Column(db.Integer, default=0)
    company_name = db.Column(db.String(250), nullable=False, default='XYZ')
    gst_no = db.Column(db.Integer, nullable=False, default=0)
    cin_no = db.Column(db.Integer, nullable=False, default=0)
    bio = db.Column(db.String, default='False')
    createdAt = db.Column(db.String, nullable=False, default='False')
    category = db.Column(db.String, default='False')
    visibility=db.Column(db.String(80),default=True)
    niche=db.Column(db.String(2000))
    admin_data=db.Column(db.String)
    campaigns = db.relationship("Campaign", back_populates="user", cascade="all, delete-orphan")
    adds = db.relationship("Add", foreign_keys="Add.influencer_id", back_populates="influencer", cascade="all, delete-orphan")

    comments = db.relationship('Comment', back_populates='user')
    likes = db.relationship('Like', back_populates='user')


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return self.username 

login_manager.user_loader
def load_user(username):
    return User.query.get(username)    