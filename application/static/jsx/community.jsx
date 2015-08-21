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
                    communityStream.onNext({action: 'updateMembersCount', community: res.community, count: res.community.count_members});
                    self.setState({subscribed: res.subscribed});
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
                                    communityStream.onNext({action: 'updateMembersCount',  community: res.community, count: res.community.count_members});
                                    self.setState({subscribed: res.subscribed});
                                    popup.onClose();
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
        React.render( <CommunitySubscriptionButton community_id={community_id} subscribed={subscribed} status={status}/>, $(this)[0]);
    });
});