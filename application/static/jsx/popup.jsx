var popupStream = new Rx.Subject()

var PopupHolder = React.createClass({
    getInitialState: function(){
        return { popups: [], counter: 0}
    },
    componentDidMount: function(){
        var self = this
        popupStream.filter(function(data){ return data.action == 'show' }).subscribe(function(data){
            var id = self.state.counter++;
            self.state.popups.push(<Popup key={'popup_'+id} id={id} {...data.data}/>)
            self.setState({popups: self.state.popups});
        });
        popupStream.filter(function(data){ return data.action == 'close' }).subscribe(function(data){
            for(var i in self.state.popups)
                if(self.state.popups[i].props.id == data.popup.props.id)break;

            delete self.state.popups[i]
            self.setState({popups: self.state.popups});
        });
    },
    render: function(){
        return(
            <div> {this.state.popups.map(function(popup){return popup})} </div>
        )
    }
})

var Popup = React.createClass({
    statics: {
        show: function(data) {
            popupStream.onNext({action: 'show', data: data})
        }
    },
    getDefaultProps: function(){
        return {
            flash: false,
            closeButton: true,
            title: ''
        }
    },
    onClose: function(){
        popupStream.onNext({action: 'close', popup: this})
    },
    closeButton: function(){
        if(!this.props.closeButton) return null;
        return <button className="close" onClick={this.onClose}></button>
    },
    title: function(){
        return !this.props.title ? '' : <h3 className="title">{this.props.title}</h3>
    },
    buttons: function() {
        var self = this
        var buttons = this.props.buttons.map(function(button,i){
            var action = ( typeof button.action == 'function' ) ? function(){ button.action(self) } : null;
            return <button key={'popup_button_'+self.props.id+'_'+i} className={'button '+button.className} onClick={action}>{button.name}</button>
        });
        if(!!buttons) buttons = <div className="buttons">{buttons}</div>
        return buttons
    },

    render: function(){
        var wrapperClass = 'popup-wrapper' + (this.props.hidden ? ' hidden' : '')
        var windowClass = 'popup-window' + (this.props.closeButton ? ' has-close-button' : '')
        return (
            <table className={wrapperClass}>
                <tr>
                    <td>
                        <div className={windowClass}>
                            {this.closeButton()}
                            {this.title()}
                            <div className="content">{this.props.content}</div>
                            {this.buttons()}
                        </div>
                    </td>
                </tr>
            </table>
        )
    }
})
$(document).ready(function(){
    React.render( <PopupHolder/>, document.getElementById('popup'));
});