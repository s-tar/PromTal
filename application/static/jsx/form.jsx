var FieldError = React.createClass({
    render: function() {
        if(!this.props.text)
            return false
        else
            return(
                <div className="error-wrapper"><div className="error">{this.props.text}</div></div>
            )
    }
})

var Input = React.createClass({
    getInitialState: function() {
        this.props.registerField(this)
        return {error: ''};
    },
    onChange: function() {
        this.setState({error: ''})
    },
    render: function() {
        var error = !this.state.error ? '' : <FieldError text={this.state.error}/>
        return(
            <div className="field-wrapper">
                <input {...this.props} onChange={this.onChange}/>{error}
            </div>
        )
    }
});

var TextArea = React.createClass({
    getInitialState: function() {
        this.props.registerField(this)
        return {error: ''};
    },
    onChange: function() {
        this.setState({error: ''})
    },
    render: function() {
        var error = !this.state.error ? '' : <FieldError text={this.state.error}/>
        return(
            <div className="field-wrapper">
                <textarea {...this.props} onChange={this.onChange}>{this.props.children}</textarea>{error}
            </div>
        )
    }
});

var AJAXForm = React.createClass({
    fields: {},
    getInitialState: function() {
        return {errors: {}, data: {}};
    },
    registerField: function(name, index) {
        var self = this
        function _registerField(field) {
            if(!!name) {
                self.fields[name] = self.fields[name] || {}
                self.fields[name][index] = field
            }
        }
        return _registerField
    },
    onSubmit: function(e) {
        e.preventDefault();
        var self = this
        var form = $(e.target)

        $.ajax({
            type: form.attr('method') || 'POST',
            url: form.attr('action') || '',
            data: form.serialize(),

            success: function(json) {
                console.log(json)
                for(var name in json.errors)
                    for(var i in json.errors[name])
                        self.fields[name][i].setState({error: json.errors[name][i][0].message})
                if(json.status == 'ok'){
                    console.log('FORM IS OK!')
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
            var clone = React.addons.cloneWithProps(child, {registerField: self.registerField(name, index)});

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

React.render(
    <AJAXForm action="/demo_form" method="post">
        <Input type="text" name="first_name"/>
        <div>
            <span><Input type="text" name="last_name"/></span>
        </div>
        <Input type="text" name="email"/>
        <Input type="text" name="email"/>
        <TextArea name="text"></TextArea>
        <Input type="submit" value="Submit"/>
    </AJAXForm>,
    document.getElementById('test_form'))
