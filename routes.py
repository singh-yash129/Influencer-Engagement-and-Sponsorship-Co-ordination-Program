from models import *
import os
@login_manager.user_loader
def load_user(username):
    return User.query.get(username)
from sqlalchemy import event
from datetime import datetime, date


@app.route('/api/flagged_users', methods=['GET'])
@login_required
def get_flagged_users():
    flags = Flag.query.all()
    flagged_users_list = [
        {
            'flag_id': flag.flag_id,
            'flagged_user_id': flag.flagged_user_id,
            'flagger_user_id': flag.flagger_user_id,
            'reason': flag.reason,
            'created_at': flag.created_at
        }
        for flag in flags
    ]
    return jsonify(flagged_users_list)
@app.route('/flagged_users')
@login_required
def flagged_users():
    return render_template('flag.html')

@app.route('/api/unflag/<flag_id>', methods=['POST'])
@login_required
def unflag_user(flag_id):
    flag = Flag.query.get(flag_id)
    if not flag:
        return jsonify({'status': 'error', 'message': 'Flag not found'}), 404

    db.session.delete(flag)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'User unflagged successfully'})



@app.route('/view_person/<string:users>', methods=['GET', 'POST'])
def view_person(users):
    user = User.query.filter_by(username=users).first()
    post=Post.query.filter_by(user_id=users).all()
    event = Event.query.filter_by(user_id=users).all()
    announce = Announce.query.filter_by(user_id=users).all()
    friend =db.session.query(Friendship,User).join(User,Friendship.user_id2==User.username).filter(Friendship.user_id2==users).all()
    follower = db.session.query(Follower,User).join(User,Follower.user_id==User.username).filter(Follower.user_id==users).all()
    posts = Post.query.filter_by(user_id=users).all()
    events = Event.query.filter_by(user_id=users).all()
    announces = Announce.query.filter_by(user_id=users).all()

# Combine all into a single list and sort by created_at
    combined = sorted(chain(posts, events, announces), key=lambda x: x.created_at, reverse=True)
    return render_template('view_person.html', user=user, post=post, event=event, announce=announce, friend=friend, follower=follower,combined=combined)
@app.route('/camp_view/<string:campaign_id>',methods=['GET','POST'])
def camp_view(campaign_id):
    camps_id=Campaign.query.filter_by(campaign_id=campaign_id).first()
    img=camps_id.image.split(',')
    user=db.session.query(User,Campaign).join(Campaign,User.username==Campaign.user_id).filter(Campaign.campaign_id==campaign_id).all()
    return render_template('camp_view.html',camps_id=camps_id,img=img,user=user)

@app.route('/inf_search',methods=['GET','POST'])
def inf_search():
    return render_template('campaign_search.html')
@app.route('/search_campaigns', methods=['GET'])
def search_campaigns():
    search_term = request.args.get('search', '')
    niche = request.args.get('niche', '')
    sort = request.args.get('sort', '')

    query = Campaign.query

    if search_term:
        query = query.filter(Campaign.title.ilike(f'%{search_term}%') | Campaign.description.ilike(f'%{search_term}%'))

    if niche:
        query = query.filter_by(niche=niche)

    if sort:
        if sort == 'start_asc':
            query = query.order_by(Campaign.start.asc())
        elif sort == 'start_desc':
            query = query.order_by(Campaign.start.desc())
        elif sort == 'budget_asc':
            query = query.order_by(Campaign.budget.asc())
        elif sort == 'budget_desc':
            query = query.order_by(Campaign.budget.desc())

    campaigns = query.all()
    results = []
    for campaign in campaigns:
        images=campaign.image.split(',')
        results.append({
            'campaign_id': campaign.campaign_id,
            'title': campaign.title,
            'description': campaign.description,
            'niche': campaign.niche,
            'start': campaign.start.strftime('%Y-%m-%d'),
            'end': campaign.end.strftime('%Y-%m-%d'),
            'target': campaign.target,
            'budget': campaign.budget,
            'goal': campaign.goal,
            'currency': campaign.currency,
            'image': images[0],
            'status': campaign.status,
            'privacy': campaign.privacy,
        })

    return jsonify(results)
@app.route('/search_admin', methods=['GET'])
def admin_search():
    query = request.args.get('query')
    filters = request.args.get('filters', '[]')
    sort = request.args.get('sort', 'asc')
    
    filters = json.loads(filters)  # Convert the filters from JSON string to list

    # Get list of flagged users for current user


    # Build the filter query based on selected filters
    filter_conditions = []
    if 'influencer' in filters:
        filter_conditions.append(User.role == 'influencer')
    if 'sponsor' in filters:
        filter_conditions.append(User.role == 'sponsor')

    # Query the users with the specified filters and excluding flagged users
    users_query = User.query.filter(
        (User.username.like(f'%{query}%') | 
         User.first_name.like(f'%{query}%') | 
         User.last_name.like(f'%{query}%'))
     
    )
    
    # Apply filters if any
    if filter_conditions:
        users_query = users_query.filter(
            db.or_(*filter_conditions)
        )
    
    # Apply sorting
    if sort == 'asc':
        users_query = users_query.order_by(User.username.asc())
    else:
        users_query = users_query.order_by(User.username.desc())

    users = users_query.all()

    return jsonify([{
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'profile_image': user.profile_picture, 
        'industry' : user.industry,
        'role' : user.role
    } for user in users])

@app.route('/admin_campaigns', methods=['GET'])
def admin_campaigns():
    search_term = request.args.get('search', '')
    niche = request.args.get('niche', '')
    sort = request.args.get('sort', '')

    query = Campaign.query

    if search_term:
        query = query.filter(Campaign.title.ilike(f'%{search_term}%') | Campaign.description.ilike(f'%{search_term}%'))

    if niche:
        query = query.filter_by(niche=niche)

    if sort:
        if sort == 'start_asc':
            query = query.order_by(Campaign.start.asc())
        elif sort == 'start_desc':
            query = query.order_by(Campaign.start.desc())
        elif sort == 'budget_asc':
            query = query.order_by(Campaign.budget.asc())
        elif sort == 'budget_desc':
            query = query.order_by(Campaign.budget.desc())

    campaigns = query.all()
    results = []
    for campaign in campaigns:
        images=campaign.image.split(',')
        results.append({
            'user_id': campaign.user_id,
            'campaign_id': campaign.campaign_id,
            'title': campaign.title,
            'description': campaign.description,
            'niche': campaign.niche,
            'start': campaign.start.strftime('%Y-%m-%d'),
            'end': campaign.end.strftime('%Y-%m-%d'),
            'target': campaign.target,
            'budget': campaign.budget,
            'goal': campaign.goal,
            'currency': campaign.currency,
            'image': images[0],
            'status': campaign.status,
            'privacy': campaign.privacy,
        })

    return jsonify(results)
@app.route('/admin/<userId>/<campaignId>/<action>/<role>', methods=['GET', 'POST'])
def admin_flagged(userId, campaignId, action, role):
    # Fetch the existing admin flag record
    admin = AdminFlag.query.filter_by(user_id=userId, campaign_id=campaignId).first()
    
    # Handle cases based on the presence of the admin record
    if not admin:
        if action == 'flagged':
            # Create a new record if it does not exist and the action is 'flagged'
            admin = AdminFlag(user_id=userId, campaign_id=campaignId, role=role, flag='flagged')
            db.session.add(admin)
            db.session.commit()
            return jsonify({"message": f"Record created and flagged for user {userId} on campaign {campaignId}"}), 200
        else:
            # If admin does not exist and action is not 'flagged', return an error
            return jsonify({"message": "Record not found and invalid action"}), 400
    
    # Update the existing record based on the action
    if action == 'flagged':
        admin.flag = 'flagged'
    elif action == 'unflagged':
        admin.flag = 'unflagged'
        db.session.delete(admin)
    else:
        return jsonify({"message": "Invalid action"}), 400
    
    # Commit the changes to the database
    db.session.commit()
    
    # Return a success response
    return jsonify({"message": f"Action {action} performed for user {userId} on campaign {campaignId}"}), 200



@app.route('/send_request_inf', methods=['POST'])
def send_request_inf():
    campaign_id = request.form['campaign_id']
    pay=Campaign.query.filter_by(campaign_id=campaign_id).first()
    user_id = current_user.username 
    request_id=str(uuid.uuid4()) # Assuming the user is logged in and user_id is available

    # Check if the request already exists
    existing_request = Add.query.filter_by(campaign_id=campaign_id, influencer_id=user_id).first()
    if existing_request:
        return jsonify({'message': 'You have already sent a request for this campaign.'}), 400

    # Create a new request
    new_request = Add(
        request_id=request_id,
        campaign_id=campaign_id,
        influencer_id=user_id,
        sponsor_id=Campaign.query.get(campaign_id).user_id,
        payment_amount=pay.budget,
        status="request"
    )
    db.session.add(new_request)
    db.session.commit()

    return jsonify({'message': 'Request sent successfully!'})
@app.route('/request/<string:request_id>/<string:action>', methods=['POST'])
def campaigned_request(request_id, action):
    # Fetch the Add record based on the campaign ID
    add = Add.query.filter_by(request_id=request_id).first()
    if not add:
        return jsonify({"status": "error", "message": "Request not found"}), 404

    # Handle different actions
    if action == 'withdraw':
        # If withdraw action, delete the Add record
        db.session.delete(add)
        db.session.commit()
        return jsonify({"status": "success", "message": "Campaign request withdrawn successfully"}), 200

    elif action == 'accept':
        # If accept action, update the payment amount and status
        if add.revised_payment:
            add.payment_amount = add.revised_payment
        pay = Payments(
            user_id=add.influencer_id,
            transaction_id=str(uuid.uuid4()),
            campaign_id=add.campaign_id,
            status="Pending",
            amount=add.payment_amount,
            sponsor=add.sponsor_id
        )

        db.session.add(pay)   
        add.status = 'pending'
        add.revised_payment = None  # Clear the revised payment after acceptance

    elif action == 'reject':
        # If reject action, reset the revised payment and set status to pending
        add.revised_payment = 0
        add.status = 'pending'
    
    elif action == 'assigned':
        # If reject action, reset the revised payment and set status to pending
        add.revised_payment = 0
        add.status = 'accepted'  
        pay = Payments(
            user_id=add.influencer_id,
            transaction_id=str(uuid.uuid4()),
            campaign_id=add.campaign_id,
            status="accepted",
            amount=add.payment_amount,
            sponsor=add.sponsor_id
        )

        db.session.add(pay)  
    else:
        return jsonify({"status": "error", "message": "Invalid action"}), 400

    db.session.commit()
    return jsonify({"status": "success", "message": f"Campaign {action}ed successfully"}), 200

@app.route('/request/<string:request_id>/negotiate', methods=['POST'])
def negotiate(request_id):
    data = request.get_json()
    revised_payment = data.get('revised_payment')
    message = data.get('message')

    # Fetch the Add record based on the campaign ID
    add = Add.query.filter_by(request_id=request_id).first()
    if not add:
        return jsonify({"status": "error", "message": "Request not found"}), 404

    # Update the record
    add.revised_payment = revised_payment

    add.message = message  
    add.status = 'pending'

    db.session.commit()
    return jsonify({"status": "success", "message": "Negotiation details updated successfully"}), 200



@app.route('/request/<string:request_id>/fixed', methods=['POST'])
def fixed(request_id):
    data = request.get_json()
    revised_payment = data.get('revised_payment')
    message = data.get('message')

    # Fetch the Add record based on the campaign ID
    add = Add.query.filter_by(request_id=request_id).first()
    if not add:
        return jsonify({"status": "error", "message": "Request not found"}), 404

    # Update the record
    add.revised_payment = revised_payment
    add.payment_amount = revised_payment
    add.message = message
    add.status = 'fixed'

    db.session.commit()
    return jsonify({"status": "success", "message": "Campaign marked as fixed"}), 200






@app.route('/spon/request/<string:user>',methods=['GET','POST'])
def spon_req(user):
    # Query to join Add and Campaign tables and filter by sponsor_id
    adds = db.session.query(Add, Campaign, User).join(Campaign, Add.campaign_id == Campaign.campaign_id).join(User, Add.influencer_id == User.username).filter(Add.sponsor_id == user).all()
    for add in adds:
        print(add)  
    return render_template('spon_request.html', adds=adds)

@app.route('/like/<content_type>/<content_id>', methods=['POST'])
def like_content(content_type, content_id):
    user_id = request.form.get('user_id')
    
    if not user_id or not content_id or content_type not in ['post', 'event', 'announce']:
        return jsonify({'message': 'Invalid request', 'status': 'error'}), 400
    
    # Check if content exists
    model = get_model_for_content_type(content_type)
    if not model.query.get(content_id):
        return jsonify({'message': 'Content not found', 'status': 'error'}), 404

    existing_like = Like.query.filter_by(content_type=content_type, content_id=content_id, user_id=user_id).first()
    
    if existing_like:
        db.session.delete(existing_like)
        db.session.commit()
        return jsonify({'message': 'Content unliked', 'status': 'unliked'})
    
    new_like = Like(content_type=content_type, content_id=content_id, user_id=user_id)
    db.session.add(new_like)
    db.session.commit()
    
    return jsonify({'message': 'Content liked', 'status': 'liked'})


@app.route('/comment/<content_type>/<content_id>', methods=['POST'])
def comment_content(content_type, content_id):
    user_id = request.form.get('user_id')
    content = request.form.get('content')
    
    if not user_id or not content or not content_id or content_type not in ['post', 'event', 'announce']:
        return jsonify({'message': 'Invalid request', 'status': 'error'}), 400
    
    # Check if content exists
    model = get_model_for_content_type(content_type)
    if not model.query.get(content_id):
        return jsonify({'message': 'Content not found', 'status': 'error'}), 404
    
    new_comment = Comment(content_type=content_type, content_id=content_id, user_id=user_id, content=content)
    db.session.add(new_comment)
    db.session.commit()
    
    return jsonify({
        'message': 'Comment added',
        'comment_id': new_comment.comment_id,
        'content': new_comment.content,
        'user_id': new_comment.user_id,
        'created_at': new_comment.created_at.isoformat()
    })


@app.route('/comments/<content_type>/<content_id>', methods=['GET'])
def get_comments(content_type, content_id):
    if content_type not in ['post', 'event', 'announce']:
        return jsonify({'message': 'Invalid content type', 'status': 'error'}), 400
    
    model = get_model_for_content_type(content_type)
    if not model.query.get(content_id):
        return jsonify({'message': 'Content not found', 'status': 'error'}), 404
    
    comments = Comment.query.filter_by(content_type=content_type, content_id=content_id).order_by(Comment.created_at.desc()).all()
    
    return jsonify([{
        'comment_id': comment.comment_id,
        'user_id': comment.user_id,
        'content': comment.content,
        'created_at': comment.created_at.isoformat()
    } for comment in comments])

# Helper function to get model based on content type
def get_model_for_content_type(content_type):
    if content_type == 'post':
        return Post
    elif content_type == 'event':
        return Event
    elif content_type == 'announce':
        return Announce
    else:
        raise ValueError('Invalid content type')
@app.route('/campaign_request/<string:request_id>/<string:action>', methods=['POST'])
def handle_campaign_request(request_id, action):
    add = Add.query.filter_by(request_id=request_id).first()
    if not add:
        return jsonify({"status": "error", "message": "Request not found"}), 404

    if action == 'accept':
        add.status = 'accepted'
        pay = Payments(
            user_id=add.influencer_id,
            transaction_id=str(uuid.uuid4()),
            campaign_id=add.campaign_id,
            status="accepted",
            amount=add.payment_amount,
            sponsor=add.sponsor_id
        )

        db.session.add(pay)
    elif action == 'reject':
        add.status = 'rejected'
    elif action == 'flag':
        add.flagged = 'flagged'
        add.status='flagged'
    elif action =='cancel':
        db.session.delete(add)
    else:
        return jsonify({"status": "error", "message": "Invalid action"}), 400

    db.session.commit()
    return jsonify({"status": "success", "message": f"Campaign {action}ed successfully"}), 200

@app.route('/campaign_request/negotiate/<string:request_id>', methods=['POST'])
def negotiate_campaign(request_id):
    data = request.get_json()
    revised_payment = data.get('revised_payment')
    negotiation_message = data.get('message')

    add = Add.query.filter_by(request_id=request_id).first()
    if not add:
        return jsonify({"status": "error", "message": "Request not found"}), 404

    add.revised_payment = revised_payment
    add.messages = negotiation_message
    add.status = 'negotiation'


    db.session.commit()

    return jsonify({"status": "success", "message": "Negotiation sent successfully"}), 200
@app.route('/send-request', methods=['POST'])
def send_request():
    data = request.get_json()
    campaign_id = data.get('campaign_id')
    influencers = data.get('influencers', [])
    spon=data.get('sponsors')
    pay=Campaign.query.filter_by(campaign_id=campaign_id).first()

    if campaign_id and influencers:
        for influencer_username in influencers:
            add = Add(
                request_id=str(uuid.uuid4()),
                campaign_id=campaign_id,
                influencer_id=influencer_username,
                status="pending",
                payment_amount=pay.budget,
                sponsor_id=spon,
            )
            db.session.add(add)
        db.session.commit()

        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 400

@app.route('/find',methods=['GET',"POST"])
def find():
    return render_template('find.html')
@app.route('/friend_request/<string:user>',methods=['GET','POST'])
def request_user(user):
    friend_requests = db.session.query(FriendRequest, User).join(User, FriendRequest.sender_id == User.username).filter(FriendRequest.receiver_id == user).all()
    users = [request.sender_id for request, _ in friend_requests]
    sender_users = User.query.filter(User.username.in_(users)).all()
    adds=db.session.query(Add, Campaign).join(Campaign, Add.campaign_id == Campaign.campaign_id).filter(Add.influencer_id == user).all()
    camps = [re.campaign_id for re, _ in adds]
    campaign=Campaign.query.filter(Campaign.campaign_id.in_(camps)).all()
    friend=db.session.query(FriendRequest,User).join(User,FriendRequest.sender_id==User.username).filter(FriendRequest.sender_id==user).all()
    return render_template('friends.html', users=sender_users, friend_requests=friend_requests,campaign=campaign,adds=adds,friends=friend)
import json
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    filters = request.args.get('filters', '[]')
    sort = request.args.get('sort', 'asc')
    
    filters = json.loads(filters)  # Convert the filters from JSON string to list

    # Get list of flagged users for current user
    flagged_users = Flag.query.filter_by(flagger_user_id=current_user.username).all()
    flagged_usernames = [flag.flagged_user_id for flag in flagged_users]

    # Build the filter query based on selected filters
    filter_conditions = []
    if 'influencer' in filters:
        filter_conditions.append(User.role == 'influencer')
    if 'sponsor' in filters:
        filter_conditions.append(User.role == 'sponsor')

    # Query the users with the specified filters and excluding flagged users
    users_query = User.query.filter(
        (User.username.like(f'%{query}%') | 
         User.first_name.like(f'%{query}%') | 
         User.last_name.like(f'%{query}%'))
        & (User.username != current_user.username) &
        (~User.username.in_(flagged_usernames))
    )
    
    # Apply filters if any
    if filter_conditions:
        users_query = users_query.filter(
            db.or_(*filter_conditions)
        )
    
    # Apply sorting
    if sort == 'asc':
        users_query = users_query.order_by(User.username.asc())
    else:
        users_query = users_query.order_by(User.username.desc())

    users = users_query.all()

    return jsonify([{
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'profile_image': user.profile_picture, 
        'industry' : user.industry,
        'role' : user.role
    } for user in users])


@app.route('/search/camp', methods=['GET'])
def camp_search():
    query = request.args.get('query')
    if query:
        # Get list of flagged users for current user
        flagged_users = Flag.query.filter_by(flagger_user_id=current_user.username).all()
        flagged_usernames = [flag.flagged_user_id for flag in flagged_users]

        # Exclude flagged users and current user from search results
        users = User.query.filter(
            (User.username.like(f'%{query}%') | 
             User.first_name.like(f'%{query}%') | 
             User.last_name.like(f'%{query}%'))
            & (User.username != current_user.username) &(User.role == 'influencer') &
            (~User.username.in_(flagged_usernames))
        ).all()

        return jsonify([{
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name
        } for user in users])
    return jsonify([])
@app.route('/send_friend_request', methods=['POST'])
def send_friend_request():
    sender_id = request.json.get('sender_id')
    receiver_id = request.json.get('receiver_id')
    if sender_id and receiver_id:
        existing_request = FriendRequest.query.filter_by(sender_id=sender_id, receiver_id=receiver_id).first()
        if not existing_request:
            friend_request = FriendRequest(sender_id=sender_id, receiver_id=receiver_id, status='pending')
            db.session.add(friend_request)
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'Friend request sent'})
    return jsonify({'status': 'error', 'message': 'Friend request failed'})

@app.route('/follow_user', methods=['POST'])
def follow_user():
    user_id = request.json.get('user_id')
    follower_user_id = request.json.get('follower_user_id')
    if user_id and follower_user_id:
        existing_follow = Follower.query.filter_by(user_id=user_id, follower_user_id=follower_user_id).first()
        if not existing_follow:
            follow = Follower(user_id=user_id, follower_user_id=follower_user_id)
            db.session.add(follow)
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'Followed user'})
    return jsonify({'status': 'error', 'message': 'Follow failed'})

@app.route('/friend_request/<int:request_id>/cancel', methods=['POST'])
@login_required
def cancel_friend_request(request_id):
    friend_request = FriendRequest.query.get(request_id)
    if friend_request and friend_request.sender_id == current_user.username:
        db.session.delete(friend_request)  
        db.session.commit()
        return jsonify({"status": "success", "message": "Friend request cancel."})
    return jsonify({"status": "error", "message": "Invalid request."})


@app.route('/friend_request/<int:request_id>/accept', methods=['POST'])
@login_required
def accept_friend_request(request_id):
    friend_request = FriendRequest.query.get(request_id)
    if friend_request and friend_request.receiver_id == current_user.username:
        # Create Friendship record
        friendship = Friendship(
            
            user_id1=friend_request.sender_id,
            user_id2=friend_request.receiver_id
        )
        db.session.add(friendship)
        
        # Delete FriendRequest record
        db.session.delete(friend_request)
        
        db.session.commit()
        return jsonify({"status": "success", "message": "Friend request accepted."})
    return jsonify({"status": "error", "message": "Invalid request."})

@app.route('/friend_request/<int:request_id>/reject', methods=['POST'])
@login_required
def reject_friend_request(request_id):
    friend_request = FriendRequest.query.get(request_id)
    if friend_request and friend_request.receiver_id == current_user.username:
        # Delete FriendRequest record
        db.session.delete(friend_request)
        db.session.commit()
        return jsonify({"status": "success", "message": "Friend request rejected."})
    return jsonify({"status": "error", "message": "Invalid request."})

@app.route('/friend_request/<int:request_id>/flag', methods=['POST'])
@login_required
def flag_friend_request(request_id):
    friend_request = FriendRequest.query.get(request_id)
    if friend_request and friend_request.receiver_id == current_user.username:
        flag_id = str(uuid.uuid4())
        flag = Flag(
            flag_id=flag_id,
            flagged_user_id=friend_request.sender_id,
            flagger_user_id=current_user.username,
            reason='flagged by own'
        )
        db.session.add(flag)
        
        # Delete FriendRequest record
        db.session.delete(friend_request)
        
        db.session.commit()
        return jsonify({"status": "success", "message": "Friend request flagged."})
    return jsonify({"status": "error", "message": "Invalid request."})

def save_file(file):
    if file:
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return filepath
    else:
        return None
@app.route('/help', methods=["POST", "GET"])
def help():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        issue = request.form['issue']
        description = request.form['description']

        new_issue = Help(
            Name=name,
            subject=issue,
            email=email,
            problem=description,
            status='under_investigation',
            issue_id=str(uuid.uuid4()),
        )
        db.session.add(new_issue)
        db.session.commit()
        return render_template('success.html', data='Your request is submitted, we will reach you soon.', id=new_issue.issue_id)
    return render_template('help.html')

@app.route("/logout")
@login_required
def logout():
    user=User.query.filter_by(username=current_user.username).first()
    user.activity='offline'
    db.session.commit()
    logout_user() 
    session.pop('user_id', None)
    return redirect(url_for('login'))

def send_otp(email, otp):
    msg = Message('OTP-Verification', recipients=[email])
    msg.body = f'Your verification code is: {otp}. Please enter this code on the website to confirm your identity. This code will expire in 10 minutes. For security, never share this code with anyone.'
    mail.send(msg)

@app.route('/forgot', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        data = request.get_json()
        action = data.get('action')

        if action == 'verifyEmail':
            email_1 = data.get('email')
            user = User.query.filter_by(email_id=email_1).first()
            if user:
                session['email'] = email_1
                return jsonify({'exists': True})
            else:
                return jsonify({'exists': False})

        elif action == 'requestOTP':
            email_1 = session.get('email')
            user = User.query.filter_by(email_id=email_1).first()
            new_pass = data.get('newPassword')
            if user:
                otp = ''.join(random.choices('0123456789', k=6))
                send_otp(user.email_id, otp)
                session['otp'] = otp
                session['new_password'] = new_pass
                return jsonify({'status': 'otp_sent'})
            else:
                return jsonify({'status': 'email_not_found'})

        elif action == 'setPassword':
            email_1 = session.get('email')
            user = User.query.filter_by(email_id=email_1).first()
            new_pass = session.get('new_password')
            passcode = data.get('passcode')

            if user and passcode == session.get('otp'):
                user.set_password(new_pass) 
                db.session.commit()
                return jsonify({'success': True})
            else:
                return jsonify({'success': False, 'message': 'Invalid passcode or user'})

    return render_template('forgot.html')


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/signup/<string:data>", methods=['GET', 'POST'])
def signup(data):
    role = 'sponsor' if data == 'sponsor' else 'influencer'
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form['email']
        username = request.form['username']
        gender = request.form.get('gender')
        dob_str = request.form.get('dob')
        dob = None if dob_str == '' else datetime.strptime(dob_str, '%Y-%m-%d').date()
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        industry = request.form.get('industry','None') if role == 'sponsor' else 'None'
        category = request.form.get('category','None') if role == 'sponsor' else 'None'
        createdAt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        company_name = request.form.get('company_name', '') if role == 'sponsor' else ''
        gst_no = request.form.get('gst_no', 0) if role == 'sponsor' else 0
        cin_no = request.form.get('cin_no', 0) if role == 'sponsor' else 0

        platforms = {
            'platform_instagram': 'instagram' in request.form.getlist('platforms'),
            'platform_youtube': 'youtube' in request.form.getlist('platforms'),
            'platform_twitter': 'twitter' in request.form.getlist('platforms'),
            'platform_facebook': 'facebook' in request.form.getlist('platforms'),
            'platform_linkedin': 'linkedin' in request.form.getlist('platforms')
        }

        if password != confirm_password:
            return render_template(f"{role}_reg.html", error="Passwords do not match")

        existing_user = User.query.filter((User.username == username) | (User.email_id == email)).first()
        if existing_user is None:
            otp = ''.join(random.choices('0123456789', k=6))
            send_otp(email, otp)

            session['new_user_data'] = {
                'createdAt': createdAt,
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'industry': industry,
                'username': username,
                'gender': gender,
                'dob': dob,
                'password': password,
                'role': role,
                'platform_youtube': platforms['platform_youtube'],
                'platform_linkedin': platforms['platform_linkedin'],
                'platform_instagram': platforms['platform_instagram'],
                'platform_facebook': platforms['platform_facebook'],
                'platform_twitter': platforms['platform_twitter'],
                'category': category,
                'company_name': company_name,
                'gst_no': gst_no,
                'cin_no': cin_no
            }
            session['otp'] = otp
            session['otp_time'] = datetime.now()

            return redirect(url_for('otp_verification'))
        else:
            return render_template(f"{role}_reg.html", error="User already exists")

    return render_template(f"{role}_reg.html")

@app.route("/otp-verification", methods=['GET', 'POST'])
def otp_verification():
    if request.method == 'POST':
        entered_otp = ''.join(request.form.get(f'otp{i}', '') for i in range(1, 7))
        otp = session.get('otp')
        otp_time = session.get('otp_time')

        if entered_otp == otp:
            otp_time = otp_time.replace(tzinfo=pytz.utc)
            current_time = datetime.now(pytz.utc)
            elapsed_time = current_time - otp_time
            if elapsed_time > timedelta(minutes=10):
                return render_template("otp.html", error="OTP has expired. Please try again.")

            session.pop('otp', None)
            session.pop('otp_time', None)

            user_data = session.get('new_user_data')
            new_user = User(
                createdAt=user_data['createdAt'],
                username=user_data['username'],
                email_id=user_data['email'],
                first_name=user_data.get('first_name'),
                last_name=user_data.get('last_name'),
                gender=user_data.get('gender'),
                dob=user_data.get('dob'),
                industry=user_data.get('industry','None'),
                role=user_data['role'],
                platform_youtube=user_data['platform_youtube'],
                platform_linkedin=user_data['platform_linkedin'],
                platform_instagram=user_data['platform_instagram'],
                platform_facebook=user_data['platform_facebook'],
                platform_twitter=user_data['platform_twitter'],
                category=user_data.get('category','None'),
                company_name=user_data.get('company_name', ''),
                gst_no=user_data.get('gst_no', 0),
                cin_no=user_data.get('cin_no', 0)
            )
            new_user.set_password(user_data['password'])
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('login'))
        else:
            return render_template("otp.html", error="Invalid OTP. Please try again.")

    return render_template("otp.html")
@app.route('/admin_pay',methods=['GET',"POST"])
def admin_payment():
    adds=Add.query.all()
    payments=Payments.query.all()
    return render_template('admin_pay.html',adds=adds,payments=payments)
@app.route("/login", methods=['GET', 'POST'])
def login():
    login_manager.login_view = 'login'
    if request.method == 'POST':
        username = request.form['uname']
        password = request.form['psw']
        slider_value = request.form['slider_value']
        user_admin_value = request.form['user_admin_value']
        print(f"Username: {username}, Password: {password}, Slider Value: {slider_value}, User/Admin: {user_admin_value}")
        
        user = User.query.filter((User.username == username) | (User.email_id == username)).first()
        if user_admin_value.lower() == 'admin':
            if username == os.getenv('ADMIN_USERNAME') and password == os.getenv('ADMIN_PASSWORD'):
                return redirect(url_for('admin_dashboard'))
            else:
                error_1 = '!! Invalid credential !!'
                return render_template("error.html", error_1=error_1)

        elif user_admin_value.lower() == 'user':
            if user and user.check_password(password) and slider_value.lower() == user.role:
                if user.two_factor_enabled == 'True':
                    if 'inp-1' in request.form:
                        verify_2fa = ''.join(request.form.get(f'inp-{i}', '') for i in range(1, 7))
                        if int(verify_2fa) == user.passcode:
                            login_user(user)
                            user.activity = 'online'
                            db.session.commit()
                            return redirect(url_for(f'{slider_value.lower()}_dashboard', user_1=user.username))
                        else:
                            error_1 = 'Invalid 2FA code!'
                            return render_template("error.html", error_1=error_1)
                    else:
                        return render_template("login.html", user=user)
                else:
                    login_user(user)
                    user.activity = 'online'
                    db.session.commit()
                    return redirect(url_for(f'{slider_value.lower()}_dashboard', user_1=user.username))
            else:
                error_1 = 'Invalid credential !!'
                return render_template("error.html", error_1=error_1)

    return render_template("login.html", user=current_user)
from itertools import chain
@app.route("/influencer_dashboard/<string:user_1>",methods=['GET','POST']) 
@login_required     
def influencer_dashboard(user_1):
    add=db.session.query(Add,Campaign).join(Campaign,Add.campaign_id==Campaign.campaign_id).filter(Add.influencer_id==user_1).all()
    inf=User.query.filter_by(username=user_1).first()
    friends = Friendship.query.filter(
        (Friendship.user_id1 == user_1) | 
        (Friendship.user_id2 == user_1)
    ).all()
    
# Extract friend IDs
    friend_ids = []
    for friend in friends:
        if friend.user_id1 == user_1:
            friend_ids.append(friend.user_id2)
        else:
            friend_ids.append(friend.user_id1)

#     Fetch posts, events, and announces for the user and their friends
    posts = Post.query.filter(Post.user_id.in_([user_1] + friend_ids)).all()
    events = Event.query.filter(Event.user_id.in_([user_1] + friend_ids)).all()
    announces = Announce.query.filter(Announce.user_id.in_([user_1] + friend_ids)).all()

# Combine all into a single list and sort by `created_at`
    combined = sorted(
        chain(posts, events, announces), 
        key=lambda x: x.created_at, 
        reverse=True
    )
    camp = Campaign.query.all()
    if request.method == "POST":
        if 'visibility' in request.form:
            visibility = request.form['visibility']
            inf.visibility = visibility
            db.session.commit()
            flash('Profile visibility updated successfully', 'success')   

        elif 'setup' in request.form:
            print('clicked')
            passcode = ''.join(request.form.get(f'inp_{i}', '') for i in range(1, 7))
            cnf_passcode = ''.join(request.form.get(f'inp_{i}', '') for i in range(7, 13))
            if passcode == cnf_passcode:
                inf.two_factor_enabled = request.form['verify']
                inf.passcode = int(passcode)
                db.session.commit()
                flash('Two-factor authentication enabled successfully.', 'success')
            else:
                flash('Passcodes do not match. Please try again.', 'danger')
        elif 'disable' in request.form:
            old_passcode = ''.join(request.form.get(f'inp_{i}', '') for i in range(13, 19))
            if int(old_passcode) == inf.passcode:
                inf.two_factor_enabled = request.form['verify']
                inf.passcode = 0
                db.session.commit()
                flash('Two-factor authentication disabled successfully.', 'success')
            else:
                flash('Incorrect passcode. Please try again.', 'danger')  
    return render_template("influencer_dashboard.html",inf=inf,post=post,add=add,camp=camp,combined=combined)   
@app.route('/profile/<string:user>',methods=["GET","POST"])
def profile(user):
    inf=User.query.filter_by(username=user).first()  
    friendships = Friendship.query.filter_by(user_id2=current_user.username).all()
    friend_ids = [friendship.user_id1 for friendship in friendships]
    friends_with_details = db.session.query(User, Friendship).join(Friendship, User.username == Friendship.user_id1).filter(User.username.in_(friend_ids)).all()
    followes=Follower.query.filter_by(follower_user_id=current_user.username).all()
    follower_ids = [follower.user_id for follower in followes]
    follower_with_details = db.session.query(User, Follower).join(Follower, User.username == Follower.user_id).filter(User.username.in_(follower_ids)).all()
    camps=db.session.query(Add,Campaign).join(Campaign,Add.campaign_id==Campaign.campaign_id).filter(Add.influencer_id==user,Add.status =='accepted').all()
    posts = Post.query.filter_by(user_id=user).all()
    events = Event.query.filter_by(user_id=user).all()
    announces = Announce.query.filter_by(user_id=user).all()

# Combine all into a single list and sort by created_at
    combined = sorted(chain(posts, events, announces), key=lambda x: x.created_at, reverse=True)

    if request.method == "POST":
        if 'upload_profile' in request.form:
            print("Upload Profile button clicked")
            if 'profile_picture' in request.files:
                pic = request.files["profile_picture"]
                if pic:

                    inf.profile_picture = save_file(pic)
                    db.session.commit()
                    flash('Profile picture uploaded successfully', 'success')
                else:
                    flash('No picture uploaded', 'warning')

        elif 'remove_profile' in request.form:
            print("Remove Profile button clicked")
            if inf.profile_picture:
                profile_picture_path = inf.profile_picture
                if os.path.exists(profile_picture_path):
                    try:
                        os.remove(profile_picture_path)
                        inf.profile_picture = None
                        db.session.commit()
                        flash('Profile picture removed successfully', 'success')
                    except OSError as e:
                        flash(f"Error deleting profile picture: {e}", 'danger')
                else:
                    flash('Profile picture not found.', 'danger')
            else:
                flash('No profile picture to remove.', 'warning')
    return render_template('inf.html',inf=inf,friends=friends_with_details,follower=follower_with_details,camps=camps,combined=combined)

@app.route("/sponsor_dashboard/<string:user_1>", methods=['GET', 'POST'])
@login_required
def sponsor_dashboard(user_1):
    camp=Campaign.query.filter_by(user_id=user_1).all()
    spo = User.query.filter_by(username=user_1).first()
    if request.method == "POST":
        if 'visibility' in request.form:
            visibility = request.form['visibility']
            spo.visibility = visibility
            db.session.commit()
            flash('Profile visibility updated successfully', 'success')   
        elif 'upload_profile' in request.form:
            print("Upload Profile button clicked")
            if 'profile_picture' in request.files:
                pic = request.files["profile_picture"]
                if pic:

                    spo.profile_picture = save_file(pic)
                    db.session.commit()
                    flash('Profile picture uploaded successfully', 'success')
                else:
                    flash('No picture uploaded', 'warning')

        elif 'remove_profile' in request.form:
            print("Remove Profile button clicked")
            if spo.profile_picture:
                profile_picture_path = spo.profile_picture
                if os.path.exists(profile_picture_path):
                    try:
                        os.remove(profile_picture_path)
                        spo.profile_picture = None
                        db.session.commit()
                        flash('Profile picture removed successfully', 'success')
                    except OSError as e:
                        flash(f"Error deleting profile picture: {e}", 'danger')
                else:
                    flash('Profile picture not found.', 'danger')
            else:
                flash('No profile picture to remove.', 'warning')
        elif 'setup' in request.form:
            print('clicked')
            passcode = ''.join(request.form.get(f'inp_{i}', '') for i in range(1, 7))
            cnf_passcode = ''.join(request.form.get(f'inp_{i}', '') for i in range(7, 13))
            if passcode == cnf_passcode:
                spo.two_factor_enabled = request.form['verify']
                spo.passcode = int(passcode)
                db.session.commit()
                flash('Two-factor authentication enabled successfully.', 'success')
            else:
                flash('Passcodes do not match. Please try again.', 'danger')
        elif 'disable' in request.form:
            old_passcode = ''.join(request.form.get(f'inp_{i}', '') for i in range(13, 19))
            if int(old_passcode) == spo.passcode:
                spo.two_factor_enabled = request.form['verify']
                spo.passcode = 0
                db.session.commit()
                flash('Two-factor authentication disabled successfully.', 'success')
            else:
                flash('Incorrect passcode. Please try again.', 'danger')

    return render_template("sponsor_dashboard.html", spo=spo,camp=camp)



@app.route('/change-password/<string:user>',methods=['GET','POST'])
def change_password(user):
    user_2=User.query.filter_by(username=user).first()
    old_pass=request.form['old_pass']
    new_pass=request.form['new_pass']
    cnf_pass=request.form['cnf_pass']
    if user_2.check_password(old_pass):
        if new_pass == cnf_pass:
            user_2.set_password(new_pass)
            db.session.commit()
            return redirect(url_for(f'{user_2.role}_dashboard',user_1=current_user.username))
        
        
            
@app.route('/delete_account/<string:user>',methods=['GET','POST'])
def delete_account(user):
    users=User.query.filter_by(username=user).first()
    email_id=request.form['email']
    if email_id==users.email_id:
        db.session.delete(users)
        db.session.commit()
        return redirect(url_for('login'))
    
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)  

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@app.route('/admin/search',methods=['GET',"POST"])
def admin_search_all():
    flagged_items=AdminFlag.query.all()
    return render_template('admin_search.html',flagged_items=flagged_items)
@app.route('/admin/dashboard',methods=['GET','POST']) 
def admin_dashboard():
    camp=Campaign.query.all()
    return render_template('admin_dashboard.html',camp=camp) 
@app.route('/admin/list',methods=['GET','POST'])
def admin_list():
    user=User.query.all()
    flg=Flag.query.all()
    camp=Campaign.query.all()
    ads=Add.query.all()
    return render_template('admin_list.html',user=user,camp=camp,flg=flg,ads=ads,datetime=datetime) 
@app.route('/admin/<userId>/<action>',methods=['GET','POST'])
def admin_action(userId,action):
    user=User.query.filter_by(username=userId).first()
    if action == 'delete':
        db.session.delete(user)
        db.session.commit()
    elif action =='deactivate':
        user.admin_data='deactivate'
        db.session.commit()
    elif action =='mav'   :
        user.admin_data='View'
        db.session.commit()
    elif action =='activate'  :
        user.admin_data='activate'  
        db.session.commit()
    elif action == 'unview':
        user.admin_data='unview'
        db.session.commit()    
    return jsonify({"message": f"Action {action} performed for user {userId}"})      

@app.route('/<string:data>/info',methods=['GET','POST'])     
def info(data):
    if data=='admin':
        user=User.query.all()
        campaigns=Campaign.query.all()
        ads=Add.query.all()
        return render_template('info.html',user=user,campaigns=campaigns,ads=ads)
    else:
        user=User.query.filter_by(role=data)
        return render_template('info.html',user=user)
    
from sqlalchemy import extract, func
@app.route('/chart-data/<category>/admin')
def chart_data(category):
    labels = []
    data = []
    background_colors = []
    border_colors = []

    if category == 'sponsor':
        # Sponsor Analysis: Individual vs Company
        labels = ['Individual', 'Company']
        individual_count = db.session.query(func.count(User.username)).filter_by(category='individual').scalar()
        company_count = db.session.query(func.count(User.username)).filter_by(category='company').scalar()
        data = [individual_count, company_count]
        background_colors = ['rgba(54, 162, 235, 0.2)', 'rgba(255, 99, 132, 0.2)']
        border_colors = ['rgba(54, 162, 235, 1)', 'rgba(255, 99, 132, 1)']

    elif category == 'user':
        # User Analysis: Sponsor vs Influencer
        labels = ['Sponsor', 'Influencer']
        sponsor_count = db.session.query(func.count(User.username)).filter_by(role='sponsor').scalar()
        influencer_count = db.session.query(func.count(User.username)).filter_by(role='influencer').scalar()
        data = [sponsor_count, influencer_count]
        background_colors = ['rgba(75, 192, 192, 0.2)', 'rgba(153, 102, 255, 0.2)']
        border_colors = ['rgba(75, 192, 192, 1)', 'rgba(153, 102, 255, 1)']

    elif category == 'ads':
        # Ads Analysis: Pending vs Accepted vs Rejected vs Negotiated
        labels = ['Pending', 'Accepted', 'Rejected', 'Negotiated']
        pending_count = db.session.query(func.count(Add.request_id)).filter_by(status='pending').scalar()
        accepted_count = db.session.query(func.count(Add.request_id)).filter_by(status='accepted').scalar()
        rejected_count = db.session.query(func.count(Add.request_id)).filter_by(status='rejected').scalar()
        negotiated_count = db.session.query(func.count(Add.request_id)).filter_by(status='negotiation').scalar()
        data = [pending_count, accepted_count, rejected_count, negotiated_count]
        background_colors = ['rgba(255, 159, 64, 0.2)', 'rgba(54, 162, 235, 0.2)', 'rgba(255, 99, 132, 0.2)', 'rgba(75, 192, 192, 0.2)']
        border_colors = ['rgba(255, 159, 64, 1)', 'rgba(54, 162, 235, 1)', 'rgba(255, 99, 132, 1)', 'rgba(75, 192, 192, 1)']

    elif category == 'campaigns':
        # Campaign Analysis: User vs Campaigns
        labels = ['Users', 'Campaigns']
        user_count = db.session.query(func.count(User.username)).scalar()
        campaign_count = db.session.query(func.count(Campaign.campaign_id)).scalar()
        data = [user_count, campaign_count]
        background_colors = ['rgba(255, 206, 86, 0.2)', 'rgba(153, 102, 255, 0.2)']
        border_colors = ['rgba(255, 206, 86, 1)', 'rgba(153, 102, 255, 1)']

    response_data = {
        'labels': labels,
        'datasets': [{
            'label': f'{category.capitalize()} Analysis',
            'backgroundColor': background_colors,
            'borderColor': border_colors,
            'borderWidth': 1,
            'data': data
        }]
    }

    return jsonify(response_data)

@app.route('/chart-data/ads/<sponsor_id>')
def ads_analysis(sponsor_id):
    labels = ['Pending', 'Negotiation', 'Accepted', 'Rejected']
    data = []
    background_colors = ['rgba(255, 99, 132, 0.2)', 'rgba(54, 162, 235, 0.2)', 'rgba(75, 192, 192, 0.2)', 'rgba(255, 206, 86, 0.2)']
    border_colors = ['rgba(255, 99, 132, 1)', 'rgba(54, 162, 235, 1)', 'rgba(75, 192, 192, 1)', 'rgba(255, 206, 86, 1)']

    pending_count = db.session.query(func.count(Add.request_id)).filter_by(sponsor_id=sponsor_id, status='pending').scalar()
    negotiation_count = db.session.query(func.count(Add.request_id)).filter_by(sponsor_id=sponsor_id, status='negotiation').scalar()
    accepted_count = db.session.query(func.count(Add.request_id)).filter_by(sponsor_id=sponsor_id, status='accepted').scalar()
    rejected_count = db.session.query(func.count(Add.request_id)).filter_by(sponsor_id=sponsor_id, status='rejected').scalar()

    data = [pending_count, negotiation_count, accepted_count, rejected_count]

    response_data = {
        'labels': labels,
        'datasets': [{
            'label': 'Ads Status Analysis',
            'backgroundColor': background_colors,
            'borderColor': border_colors,
            'borderWidth': 1,
            'data': data
        }]
    }

    return jsonify(response_data)

# Route for Influencer Analysis 1: Influencers vs Campaigns
@app.route('/chart-data/influencer-campaigns/<sponsor_id>')
def influencer_campaigns_analysis(sponsor_id):
    labels = []
    data = []
    background_colors = []
    border_colors = []

    campaigns = db.session.query(Campaign.user_id, func.count(Campaign.campaign_id))\
                .filter_by(user_id=sponsor_id)\
                .group_by(Campaign.user_id).all()

    for campaign in campaigns:
        influencer = campaign[0]
        campaign_count = campaign[1]

        labels.append(influencer)
        data.append(campaign_count)
        background_colors.append('rgba(54, 162, 235, 0.2)')
        border_colors.append('rgba(54, 162, 235, 1)')

    response_data = {
        'labels': labels,
        'datasets': [{
            'label': 'Influencers vs Campaigns',
            'backgroundColor': background_colors,
            'borderColor': border_colors,
            'borderWidth': 1,
            'data': data
        }]
    }

    return jsonify(response_data)

# Route for Influencer Analysis 2: Influencers vs Influencers (filtered by sponsor)
@app.route('/chart-data/influencer/<sponsor_id>')
def influencer_analysis(sponsor_id):
    labels = []
    data = []
    background_colors = []
    border_colors = []

    influencers = db.session.query(User.username, func.count(Add.influencer_id))\
                  .join(Add, User.username == Add.influencer_id)\
                  .filter(Add.sponsor_id == sponsor_id)\
                  .group_by(User.username).all()

    for influencer in influencers:
        labels.append(influencer[0])
        data.append(influencer[1])
        background_colors.append('rgba(153, 102, 255, 0.2)')
        border_colors.append('rgba(153, 102, 255, 1)')

    response_data = {
        'labels': labels,
        'datasets': [{
            'label': 'Influencer vs Influencer',
            'backgroundColor': background_colors,
            'borderColor': border_colors,
            'borderWidth': 1,
            'data': data
        }]
    }

    return jsonify(response_data)

@app.route('/spo/inf/details',methods=['GET'])
def spo_inf_search():
    return render_template('spo_seacrh.html')  
@app.route('/search/inf', methods=['GET'])
def search_inf():
    query = request.args.get('query')
    filters = request.args.get('filters', '[]')
    sort = request.args.get('sort', 'asc')
    
    filters = json.loads(filters)  # Convert the filters from JSON string to list

    # Get list of flagged users for current user
    flagged_users = Flag.query.filter_by(flagger_user_id=current_user.username).all()
    flagged_usernames = [flag.flagged_user_id for flag in flagged_users]

    # Build the filter query based on selected filters
    filter_conditions = []
    if 'influencer' in filters:
        filter_conditions.append(User.role == 'influencer')
    if 'sponsor' in filters:
        filter_conditions.append(User.role == 'sponsor')

    # Query the users with the specified filters and excluding flagged users
    users_query = User.query.filter(
        (User.username.like(f'%{query}%') | 
         User.first_name.like(f'%{query}%') | 
         User.last_name.like(f'%{query}%'))
        & (User.username != current_user.username) &
        (~User.username.in_(flagged_usernames))
    )
    
    # Apply filters if any
    if filter_conditions:
        users_query = users_query.filter(
            db.or_(*filter_conditions)
        )
    
    # Apply sorting
    if sort == 'asc':
        users_query = users_query.order_by(User.username.asc())
    else:
        users_query = users_query.order_by(User.username.desc())

    users = users_query.all()

    return jsonify([{
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'profile_image': user.profile_picture, 
        'industry' : user.industry,
        'role' : user.role
    } for user in users])
 
        
@app.route('/sponsor_dashbaord/add_campaigns/<string:user>', methods=['GET', 'POST'])
def add_campaign(user):
    camp=Campaign.query.filter_by(user_id=user).all()
    if request.method == 'POST':
        user_id = request.form['user_id']
        title = request.form['title']
        description = request.form['description']
        niche = request.form['niche']
        start = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        end = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
        target = request.form['target']
        budget = request.form['budget']
        goal = request.form['goal']
        currency = request.form['currency']
        privacy = request.form['privacy']

        images = request.files.getlist('image')
        image_filenames = []
        for image in images:
            if image:
                filename = secure_filename(image.filename)
                unique_filename = str(uuid.uuid4()) + "_" + filename
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                image_filenames.append(unique_filename)

        campaign = Campaign(
            campaign_id=str(uuid.uuid4()),
            user_id=user_id,
            title=title,
            description=description,
            niche=niche,
            start=start,
            end=end,
            target=target,
            budget=budget,
            goal=goal,
            currency=currency,
            image=",".join(image_filenames),
            status='active',  
            privacy=privacy
        )
        db.session.add(campaign)
        db.session.commit()
        flash('Campaign added successfully!', 'success')
        return redirect(url_for('add_campaign',user=current_user.username)) 
 
    return render_template('campaigns.html',camp=camp)
@app.route('/view_campaigns/<string:campaign_id>',methods=['GET','POST'])
def view_campaign(campaign_id):
    camps_id=Campaign.query.filter_by(campaign_id=campaign_id).first()
    user=User.query.filter_by(username=current_user.username).first()
    img=camps_id.image.split(',')
    print(img)
    if request.method == 'POST':
    
        camps_id.title = request.form['title']
        camps_id.description = request.form['description']
        camps_id.niche = request.form['niche']
        camps_id.start = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        camps_id.end = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
        camps_id.target = request.form['target']
        camps_id.budget = request.form['budget']
        camps_id.goal = request.form['goal']
        camps_id.currency = request.form['currency']
        camps_id.privacy = request.form['privacy']



        db.session.commit()
        flash('Campaign edited successfully!', 'success')
    return render_template('campaign_view.html',camps_id=camps_id,user=user,img=img)

@app.route("/edit_data/<string:user1>", methods=['GET', 'POST'])
def edit_data(user1):
    user = User.query.filter_by(username=user1).first()
    if request.method == 'POST':
        user.first_name = request.form.get('first_name', 'None')
        user.last_name = request.form.get('last_name', 'None')
        user.dob = request.form.get('date', 'None')
        user.gender = request.form.get('gender', 'None')
        user.company_name = request.form.get('company_name', 'None')
        user.gst_no = request.form.get('gst_no', 'None')
        user.cin_no = request.form.get('cin_no', 'None')
        user.username = request.form.get('username')
        user.industry = request.form.get('industry', 'None')
        db.session.commit()
        return redirect(url_for(f'{user.role}_dashboard', user_1=current_user.username))
    return redirect(url_for(f'{user.role}_dashboard', user_1=current_user.username))
@app.route("/edit_niche/<string:user1>", methods=['GET', 'POST'])
def edit_niche(user1):
    user=User.query.filter_by(username=user1).first()
    if request.method=='POST':
        user.niche=request.form.get('niche', "  ")
        db.session.commit()
        return redirect(url_for('profile',user=current_user.username)) 
    return redirect(url_for('profile',user=current_user.username)) 
@app.route("/edit_bio/<string:user1>", methods=['GET', 'POST'])
def edit_bio(user1):
    user=User.query.filter_by(username=user1).first()
    if request.method=='POST':
        user.bio=request.form.get('bio', "  ")
        db.session.commit()
        return redirect(url_for('profile',user=current_user.username)) 
    return redirect(url_for('profile',user=current_user.username)) 
@app.route("/view_campaigns/<string:campaign_id>/delete",methods=['GET','POSt'])
def delete_campaign(campaign_id):
    camps=Campaign.query.filter_by(campaign_id=campaign_id).first()
    if camps.image:
        img=camps.image.split(',')
        for i in img:
           file_path=os.path.join(app.config['UPLOAD_FOLDER'],i)
           os.remove(file_path)
    db.session.delete(camps)
    db.session.commit()
    return redirect(url_for('add_campaign',user=current_user.username))
@app.route('/pay/<string:transaction_id>',methods=['GET','POST'])
def pay(transaction_id):
    pay=Payments.query.filter_by(transaction_id=transaction_id).first()
    pay.status='paid'
    db.session.commit()
    return redirect(url_for('process_payment',user=pay.user_id))

@app.route('/payments/<string:user>',methods=['GET','POST'])
def payments(user):
    payments=Payments.query.filter_by(sponsor=user).all()
    return render_template('payment_history.html',payments=payments)
@app.route('/process/pay/<string:transaction_id>',methods=['GET','POST'])
def process_payment(transaction_id):
    payments=Payments.query.filter_by(transaction_id=transaction_id).first()
    return render_template('payment.html',payments=payments)
@app.route('/inf/pay/<string:user>',methods=['GET','POST'])
def inf_pay(user):
    payments=Payments.query.filter_by(influncer_id=user).all()
    return render_template('inf_pay.html',payments=payments)
@app.route('/privacy')
def privacy():
    return render_template('privacy.html')       
@app.route('/about')
def about():
    return render_template('about.html')  
@app.route('/post/<string:user>', methods=["GET", 'POST'])
def post(user):
    if request.method == 'POST':
        post_title = request.form.get('post-title', 'NA')
        post_content = request.form.get('post-content', 'NA')
        media = request.files['media']
  

        media_type = None
        media_url = None

        if media:
            if media.mimetype.startswith('image/'):
                media_type = 'image'
            elif media.mimetype.startswith('video/'):
                media_type = 'video'
            media_url = save_file(media)

        post = Post(
            user_id=user,
            post_id=str(uuid.uuid4()),
            created_at=datetime.utcnow(),
            title=post_title,
            content=post_content,
            media_type=media_type,
            media_url=media_url
        )

        db.session.add(post)
        db.session.commit()
        return redirect(url_for(f'{current_user.role}_dashboard', user_1=current_user.username))
    return redirect(url_for(f'{current_user.role}_dashboard', user_1=current_user.username))

@app.route('/event/<string:user>', methods=["GET", "POST"])
def event(user):
    if request.method == 'POST':
        title = request.form.get('event-title')
        description = request.form.get('event-description')
        date = request.form.get('event-date')
        start_time = request.form.get('event-start-time')
        end_time = request.form.get('event-end-time')
        picture = request.files['event-picture']

        media = None
        if picture:
            media = save_file(picture)

        event = Event(
            event_id=str(uuid.uuid4()),
            user_id=user,
            title=title,
            description=description,
            date=date,
            start_time=start_time,
            end_time=end_time,
            media=media,
            created_at=datetime.utcnow()
        )

        db.session.add(event)
        db.session.commit()
        return redirect(url_for(f'{current_user.role}_dashboard', user_1=current_user.username))
    return redirect(url_for(f'{current_user.role}_dashboard', user_1=current_user.username))

@app.route('/announce/<string:user>', methods=["GET", "POST"])
def announce(user):
    if request.method == "POST":
        title = request.form.get("announcement-title")
        content = request.form.get("announcement-description")
        announce = Announce(
            announce_id=str(uuid.uuid4()),
            user_id=user,
            title=title,
            content=content,
            created_at=datetime.utcnow()
        )
        db.session.add(announce)
        db.session.commit()
        return redirect(url_for(f'{current_user.role}_dashboard', user_1=current_user.username))
    return redirect(url_for(f'{current_user.role}_dashboard', user_1=current_user.username))     
@app.route('/delete_post/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    post = Post.query.get(post_id)
    if post:
        db.session.delete(post)
        db.session.commit()
        return jsonify({'message': 'Post deleted successfully'}), 200
    else:
        return jsonify({'message': 'Post not found'}), 404
@app.route("/account")
def account():
    try:
        return redirect(url_for(f'{current_user.role}_dashboard', user_1=current_user.username))
    except Exception as e:
        return render_template('error.html', error_1='Unexpected error occurred: !! Pls login to Continue !!')