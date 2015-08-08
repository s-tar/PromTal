var LikesCounter = React.createClass({
    getInitialState: function() {
        return {stream: new Rx.Subject(), processing: false, count: this.props.count || 0, active: !!this.props.my, my: this.props.my || false, hover: false}
    },
    onClick: function(){
        this.state.stream.onNext({action: 'click'})
    },
    componentWillMount: function(){
        var self = this;
        this.state.stream.filter(function(data){return data.action == 'click'}).debounce(300).subscribe(function(data){
            $.post('/vote/like', {entity: self.props.entity, entity_id: self.props.entity_id, value: !self.state.active}, "json")
                .done(function(res){
                    if(res.status == 'ok'){
                        self.setState({active: res.vote.value != '0', count: res.count});
                    }
                }).error(function(){ self.state.processing = false })
        });
    },
    render: function() {
        return(
            <div className={"likes-counter " + (this.state.active ? "active" : "")} onClick={this.onClick}>
                <span className="fa icon"></span>
                <span>{this.state.count}</span>
            </div>
        )
    }
});


$(document).ready(function(){
    $('.likes-counter-component').each(function(){
        var entity = $(this).attr('data-entity');
        var entity_id = $(this).attr('data-entity-id');
        var count = parseInt($(this).attr('data-count')) || 0;
        var my = Boolean($(this).attr('data-my-vote') == '1');
        React.render( <LikesCounter entity={entity} entity_id={entity_id} count={count} my={my}/>, $(this)[0]);
    });
});