var LikesCounter = React.createClass({
    getInitialState: function() {
        return {count: this.props.count || 0, active: !!this.props.my, my: this.props.my || false, hover: false}
    },
    onClick: function(){
        this.setState({active: !this.state.active})
    },
    render: function() {
        return(
            <div className="holder" onClick={this.onClick}>
                <span className={ "fa icon " + (this.state.active ? "active" : "'")}></span>
                <span>{this.state.count}</span>
            </div>
        )
    }
});


$(document).ready(function(){
    $('.likes-counter').each(function(){
        var entity = $(this).attr('data-entity');
        var entity_id = $(this).attr('data-entity-id');
        var count = parseInt($(this).attr('data-count')) || 0;
        var my = Boolean($(this).attr('data-my-vote'));
        React.render( <LikesCounter entity={entity} entity_id={entity_id} count={count} my={my}/>, $(this)[0]);
    });
});