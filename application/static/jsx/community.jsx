var communityStream = new Rx.Subject();
var CommunityMembersCounter = React.createClass({
    getInitialState: function() {
        return {count: this.props.count || 0}
    },
    componentWillMount: function(){
        var self = this;
        communityStream.filter(function(data){return data.action == 'updateMembersCount' && data.community.id == self.props.community_id}).subscribe(function(data){
           self.setState({count: data.count});

        });
    },
    render: function() {
        var title = 'учасников';
        var mod_count = this.state.count % 10;
        if(mod_count == 1) title = 'учасник';
        if(mod_count > 1 && mod_count < 5) title = 'учасника';
        if(this.state.count % 100 > 10 && this.state.count % 100 < 20) title = 'учасников';
        return(
            <div className="members-counter">
                <span>{this.state.count} {title}</span>
            </div>
        )
    }
});

var CommunitySubscriptionButton = React.createClass({
    getInitialState: function() {
        return {subscribed: this.props.subscribed, status: this.props.status }
    },
    onJoin: function(){
        if(this.state.subscribed) return;
        var self = this;
        $.post('/community/subscription/' + this.props.community_id, {subscription: 'subscribe'},"json")
        .done(function(res){
            if(res.status == 'ok'){
                if(res.community.type == 'private') {
                    Popup.show({ content: 'Ваша заявка принята на рассмотрение.' });
                    self.setState({subscribed: res.subscribed, status: 'waiting'});
                }else{
                     if(self.props.reload) {
                         window.location.reload()
                     }else{
                         communityStream.onNext({action: 'updateMembersCount', community: res.community, count: res.community.count_members});
                         self.setState({subscribed: res.subscribed});
                     }

                }
            }
        });
    },
    onLeave: function(){
        if(!this.state.subscribed && this.state.status != 'waiting') return;
        var self = this;
        if(this.state.status == 'waiting') {
            $.post('/community/subscription/' + self.props.community_id, {subscription: 'unsubscribe'},"json")
            .done(function(res){
                if(res.status == 'ok'){
                    communityStream.onNext({action: 'updateMembersCount',  community: res.community, count: res.community.count_members});
                    self.setState({status: undefined, subscribed: res.subscribed});
                }
            });
        }else{
            Popup.show({
                title: 'Покинуть группу',
                content: 'Вы уверены,что хотите покинуть группу?',
                closeButton: false,
                buttons: [
                    {
                        name: 'Да',
                        className: 'left',
                        action: function(popup){
                            $.post('/community/subscription/' + self.props.community_id, {subscription: 'unsubscribe'},"json")
                            .done(function(res){
                                if(res.status == 'ok'){
                                    if(self.props.reload) {
                                        window.location.reload();
                                    }else{
                                        communityStream.onNext({action: 'updateMembersCount',  community: res.community, count: res.community.count_members});
                                        self.setState({subscribed: res.subscribed});
                                        popup.onClose();
                                    }
                                }
                            });
                        }
                    },
                    {
                        name: 'Нет',
                        className: 'right',
                        action: function(popup){
                            popup.onClose()
                        }
                    },
                ]
            })
        }


    },
    componentWillMount: function(){
        var self = this;
        communityStream.filter(function(data){return data.action == 'updateMembersCount' && data.community.id == self.props.community_id}).subscribe(function(data){
           self.setState({count: data.count});
        });
    },
    render: function() {
        var status = this.state.status;
        var button = !this.state.subscribed ?
            <button className="community-join" onClick={this.onJoin}>Присоединиться</button>:
            status == 'waiting' ?
                <button className="community-leave" onClick={this.onLeave}>Отменить заявку</button> :
                <button className="community-leave" onClick={this.onLeave}>Покинуть</button>;

        return button
    }
});


var CommunityMember = React.createClass({
    getInitialState: function() {
        return {
            user: {
                id: this.props.member_id,
                full_name: this.props.member_name,
                photo: this.props.member_photo,
                description: this.props.member_description,
                status: this.props.member_status
            }
        }
    },
    sendRequest: function(type){
         var self = this;
        $.post('/community/' + this.props.community_id + '/'+type+'/member/'+ this.state.user.id, "json")
        .done(function(res){
            if(res.status == 'ok'){
                self.state.user.status = res.user.status;
                self.setState({user:  self.state.user})
            }
        });
    },
    onAccept: function(){
       this.sendRequest('accept');
    },
    onReject: function(){
        this.sendRequest('reject');
    },
    onDelete: function(){
        var self = this;
        Popup.show({
            title: 'Удалить пользователя',
            content: 'Вы уверены,что хотите удалить пользователя из группы?',
            closeButton: false,
            buttons: [
                {
                    name: 'Да',
                    className: 'left',
                    action: function(popup){
                        self.sendRequest('reject');
                        popup.onClose();
                    }
                },
                {
                    name: 'Нет',
                    className: 'right',
                    action: function(popup){
                        popup.onClose()
                    }
                },
            ]
        })
    },
    render: function() {
        var description = this.state.user.description;
        var is_owner = this.props.community_owner_id == current_user.id;

        if(!is_owner && this.state.user.status == 'waiting') return null;
        if(this.state.user.status == 'rejected') return null;

        if(is_owner){
            if(this.state.user.status == 'waiting') {
                description = (
                    <div className="buttons">
                        <a className="button" onClick={this.onAccept}>Принять</a>
                        <a className="button reject" onClick={this.onReject}>Отклонить</a>
                    </div>
                )
            }else if(this.state.user.status == 'accepted') {
                description = (
                    <div className="buttons">
                        <a className="button delete" onClick={this.onDelete}>Удалить</a>
                    </div>
                )
            }
        }
        description = description ? <div className="description">{description}</div> : null;
        return (
            <div className="member user-frame">
                <UserIcon user={this.state.user}/>
                <div className="info">
                    <div className="name"><a href={"/user/profile/" + this.state.user.id}>{this.state.user.full_name}</a></div>
                    {description}
                </div>
            </div>
        )
    }
});


$(document).ready(function(){
    $('.members-counter-component').each(function(){
        var community_id = $(this).attr('data-community-id');
        var count = parseInt($(this).attr('data-count')) || 0;
        React.render( <CommunityMembersCounter community_id={community_id} count={count}/>, $(this)[0]);
    });

    $('.community-subscription-component').each(function(){
        var community_id = $(this).attr('data-community-id');
        var subscribed = Boolean($(this).attr('data-subscribed') == 'True');
        var status = $(this).attr('data-status');
        var reload = $(this).attr('data-reload') == 'True' ? true : false;
        React.render( <CommunitySubscriptionButton community_id={community_id} subscribed={subscribed} status={status} reload={reload}/>, $(this)[0]);
    });

    $('.community-member-component').each(function(){
        var community_id = $(this).attr('data-community-id');
        var community_owner_id = $(this).attr('data-community-owner-id');
        var member_id = $(this).attr('data-member-id');
        var member_name = $(this).attr('data-member-name');
        var member_photo = $(this).attr('data-member-photo');
        var member_status = $(this).attr('data-member-status');
        var member_description = $(this).attr('data-member-description');
        React.render(
            <CommunityMember
                community_id={community_id}
                community_owner_id={community_owner_id}
                member_id={member_id}
                member_name={member_name}
                member_photo={member_photo}
                member_status={member_status}
                member_description={member_description}
            />, $(this)[0]);
    });
});