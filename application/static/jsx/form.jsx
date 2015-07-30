var FieldError = React.createClass({
    getInitialState: function() {
        this.props.registerError(this);
        return {text: ''}
    },
    render: function() {
        if(!this.state.text)
            return false
        else
            return(
               <div className='error-wrapper'><div className="error">{this.state.text}</div></div>
            )
    }
})

var Input = React.createClass({
    onChange: function(event) {
        this.refs.error.setState({text: ''})
        if(typeof this.props.onChange == 'function')
            this.props.onChange(event)
    },
    render: function() {
        return(
            <div className="field-wrapper">
                <input {...this.props} onChange={this.onChange}/>
                <FieldError ref='error' registerError={this.props.registerError}/>
            </div>
        )
    }
});

var Select = React.createClass({
    onChange: function(event) {
        this.refs.error.setState({text: ''})
        if(typeof this.props.onChange == 'function')
            this.props.onChange(event)
    },
    render: function() {
        return(
            <div className="field-wrapper">
                <select {...this.props} onChange={this.onChange}>{this.props.children}</select>
                <FieldError ref='error' registerError={this.props.registerError}/>
            </div>
        )
    }
});

var TextArea = React.createClass({
    updateHeight: function(){
        if(this.props.autosize){
            var dom = this.refs.textarea.getDOMNode();
            dom.style.height = 0
            dom.style.height =  dom.offsetHeight+ (dom.scrollHeight - dom.offsetHeight)+'px'
        }
    },
    onChange: function(event) {
        this.refs.error.setState({text: ''})
        if(typeof this.props.onChange == 'function')
            this.props.onChange(event)
    },
    componentDidMount() {
        this.updateHeight()
        if(this.props.focus)
            this.refs.textarea.getDOMNode().focus()
    },
    componentDidUpdate() {
        this.updateHeight()
    },
    render: function() {
        return(
            <div className="field-wrapper">
                <textarea ref='textarea' {...this.props} onChange={this.onChange}>{this.props.children}</textarea>
                <FieldError ref='error' registerError={this.props.registerError}/>
            </div>
        )
    }
});

var AJAXForm = React.createClass({
    getInitialState: function() {
        return {errors: {}, data: {}};
    },
    registerError: function(name, index) {
        var self = this
        self.fields = self.fields || {}
        function _registerError(field) {
            if(!!name) {
                self.fields[name] = self.fields[name] || {}
                self.fields[name][index] = field
            }
        }
        return _registerError
    },
    showErrors: function(errors) {
        for(var name in errors)
            for(var i in errors[name]) {
                var field = this.fields[name] && this.fields[name][i]
                if(!!field) field.setState({text: errors[name][i][0].message})
            }

    },
    onSubmit: function(e) {
        e.preventDefault();
        var self = this
        var form = e.target;
        $.ajax({
            type: form.getAttribute('method') || 'POST',
            url: form.getAttribute('action') || '',
            data: new FormData(form),
            cache: false,
            contentType: false,
            processData: false,

            success: function(json) {
                self.showErrors(json.errors)
                if(json.status == 'ok'){
                    if(typeof self.props.onSuccess == 'function')
                        self.props.onSuccess(json)
                }

            }
         });
    },
    childrenWithErrors: function(root, parent) {
        var self = this
        var counter = {}
        parent = parent || root

        if(typeof parent.props.children == 'string')
            return parent.props.children

        return React.Children.map(parent.props.children, function (child) {
            if(!React.isValidElement(child))return child
            var name = child.props.name
            counter[name] = counter[name] || 0
            var index = counter[name]++
            var clone = React.addons.cloneWithProps(child, {
                registerError: self.registerError(name, index)
            });

            if(!!clone.props.children)
                clone.props.children = self.childrenWithErrors(root, clone)
            return clone
        });
    },
    render: function() {
        this.children = this.childrenWithErrors(this)
        return(
            <form {...this.props} onSubmit={this.onSubmit}>{this.children}</form>
        )
    }
});

var DropDownPass = React.createClass({

    getInitialState: function(){
        return { display_inputs: 'none', drop_row: 'down' };
    },

    clicked: function(){
        if(this.state.display_inputs == 'none') {
            this.setState({display_inputs: 'block', drop_row: 'up'});
        } else {
            this.setState({display_inputs: 'none', drop_row: 'down'});
        }
        
    },

    render: function() {
        var self = this;

        var divInputs = {display: this.state.display_inputs,};
        var classRow = "glyphicon glyphicon-menu-" + this.state.drop_row;
        return (
            <div>
                <div className="drop-down-pass" onClick={self.clicked.bind(self)}>Сменить <span className={classRow}></span></div>
                <div style={divInputs}>
                    <p><input name="password_old" className="form-control" type="text" placeholder="Старый пароль"/></p>
                    <NewPass />
                </div>
            </div>
        );

    }
});

var NewPass = React.createClass({

    getInitialState: function(){
        return { password_1: '', password_2: '',
                 eye_1_password: 'password', eye_2_password: 'password',
                 eye_1_status: 'close', eye_2_status: 'close',
                 border_1_Color: '', border_2_Color: '',
                 colors: ["#f00", "#c06", "#f60", "#3c0", "#3f0"]};
    },

    password1Change: function(e){
        this.setState({password_1:e.target.value, border_1_Color:'red'});
        var password = e.target.value;
        var self = this;
        set_color = function(num_color) {
            self.setState({border_1_Color:self.state.colors[num_color]});
        }
        if (password.match(/[a-z]/)) {
            set_color(0);
        }
        if (password.match(/[A-Z]/)) {
            set_color(1);
        }
        if (password.match(/\d+/)) {
            set_color(2);
        }
        if (password.match(/(.*[0-9].*[0-9].*[0-9])/)) {
            set_color(2);
        }
        if (password.match(/.[!,@,#,$,%,^,&,*,?,_,~]/)) {
            set_color(3);
        }
        if (password.match(/(.*[!,@,#,$,%,^,&,*,?,_,~].*[!,@,#,$,%,^,&,*,?,_,~])/)) {
            set_color(3);
        }
        if (password.match(/([a-z].*[A-Z])|([A-Z].*[a-z])/)) {
            set_color(3);
        }
        if (password.match(/([a-zA-Z])/) && password.match(/([0-9])/)) {
            set_color(3);
        }
        if (password.match(/([a-zA-Z0-9].*[!,@,#,$,%,^,&,*,?,_,~])|([!,@,#,$,%,^,&,*,?,_,~].*[a-zA-Z0-9])/)) {
            set_color(4);
        }
    },

    password2Change: function(e){
        this.setState({password_2:e.target.value});
        var password = e.target.value;
        var self = this;
        set_color = function(num_color) {
            self.setState({border_2_Color:self.state.colors[num_color]});
        }
        if (password === self.state.password_1) {
            set_color(3);
        } else {
            set_color(0);
        }

    },

    clickedEye1: function(){
        if(this.state.eye_1_status == 'close') {
            this.setState({eye_1_status: 'open', eye_1_password: 'text'});
        } else {
            this.setState({eye_1_status: 'close', eye_1_password: 'password'});
        }
    },

    clickedEye2: function(){
        if(this.state.eye_2_status == 'close') {
            this.setState({eye_2_status: 'open', eye_2_password: 'text'});
        } else {
            this.setState({eye_2_status: 'close', eye_2_password: 'password'});
        }
    },

    render: function() {
        var self = this;
        var classEye = "eye-pass glyphicon glyphicon-eye-";
        var classEye1 = classEye + this.state.eye_1_status;
        var classEye2 = classEye + this.state.eye_2_status;
        var styleInput1 = {borderColor: this.state.border_1_Color,};
        var styleInput2 = {borderColor: this.state.border_2_Color,};
        return (
            <div>
                <div className="form-pass">
                    <input name="password_1" className="form-control" style={styleInput1} type={this.state.eye_1_password} value={this.state.password_1} onChange={this.password1Change} placeholder="Новый пароль"/>
                    <span className={classEye1} onClick={self.clickedEye1}></span>
                </div>
                <div className="form-pass form-pass2">
                    <input name="password_2" className="form-control" style={styleInput2} type={this.state.eye_2_password} value={this.state.password_2} onChange={this.password2Change} placeholder="Повторить новый пароль"/>
                    <span className={classEye2} onClick={self.clickedEye2}></span>
                </div>
            </div>
        );

    }
});