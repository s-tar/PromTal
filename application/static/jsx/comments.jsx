var commentsStream = new Rx.Subject();

var CommentsCounter = React.createClass({
    getInitialState: function() {
        return {count: this.props.count || 0}
    },
    componentWillMount: function(){
        var self = this
        var entity = this.props.entity
        var entity_id = this.props.entity_id

        //commentsStream.filter(function(data){ return data.action == 'update' &&
        //        data.entity == entity &&
        //        data.entity_id == entity_id })
        //    .subscribe(function(data){
        //        self.setState({count: storage.getCommentsCount()});
        //})
    },
    render: function() {
        return(
            <div><span className="fa fa-comments-o"></span>{this.state.count}</div>
        )
    }
})
var CommentForm = React.createClass({
    getDefaultProps: function(){
        return {comment: {}}
    },
    getInitialState: function() {
        return {text: '', disabled: true, stream: new Rx.Subject(), media: []}
    },
    onSuccess: function(data){
        var storage = CommentStorageFactory.get(this.props.entity, this.props.entity_id)
        this.setState({text: ''})
        if(!!this.props.root)
            this.props.root.showAnswerForm(null)
        storage.add(data.comment)
        this.state.stream.onNext({action: 'clearMedia'});
        this.updateSubmitDisabled()
    },
    onChange: function(e){
        this.state.text = e.target.value
        this.setState({text: this.state.text})
        this.state.stream.onNext({action: 'updateSubmitDisabled'});
    },
    onKeyDown: function(e){
        if(e.key == 'Enter' && e.ctrlKey && !!this.state.text.trim() && !this.state.disabled) {
            var form = this.refs.form
            e['target'] = form.getDOMNode()
            form.onSubmit(e)
        }

    },
    updateSubmitDisabled: function(){
        this.state.disabled =
            (this.refs.mediaHolder.state.count == 0 && !this.state.text) || this.refs.mediaUploader.state.opened
        this.setState({disabled: this.state.disabled })
    },
    componentWillMount: function(){
        this.state.text = this.props.comment.text
    },
    componentDidMount: function(){
        var self = this
        this.state.stream
            .filter(function(data){ return data.action == 'updateSubmitDisabled' && self.isMounted()})
            .subscribe(self.updateSubmitDisabled)
        this.updateSubmitDisabled()
    },
    render: function() {
        if(!current_user.is_authorized) return null
        var entity = this.props.entity || this.props.comment.entity
        var entity_id = this.props.entity_id || this.props.comment.entity_id

        if(!(entity && entity_id) && !this.props.quote_for && !this.props.comment) return null

        var action = !this.props.quote_for ? '/comment' : '/comment/quote'
        action += !this.props.comment.id ? '/new' : '/edit/'+this.props.comment.id

        return(
            <li className="comment form">
                <UserIcon user={current_user}/>
                <div className="message frame">
                    <div className="fa fa-caret-left arrow"></div>
                    <div className="text">
                        <AJAXForm ref='form' className="custom-form" action={action} method="post" onSuccess={this.onSuccess}>
                            <div className="wrapper">
                                <input type="hidden" name="entity_name" value={this.props.entity}/>
                                <input type="hidden" name="entity_id" value={this.props.entity_id}/>
                                <input type="hidden" name="quote_for" value={this.props.quote_for}/>
                                <TextArea ref="comment"
                                    focus={!!this.props.quote_for} name="comment"
                                    autosize={true}
                                    onKeyDown={this.onKeyDown}
                                    onChange={this.onChange}
                                    placeholder="Оставить комментарий"
                                    value={this.state.text}></TextArea>
                                <div className="right-buttons">
                                    <MediaUploader ref="mediaUploader" stream={this.state.stream} holder={this}/>
                                    <button type="submit"
                                        disabled={this.state.disabled}
                                        className="button send"
                                        title="Отправить">
                                        <span className="fa fa-send"></span>
                                    </button>
                                </div>
                                <MediaHolder ref="mediaHolder" stream={this.state.stream} holder={this}/>
                            </div>
                        </AJAXForm>
                    </div>
                </div>
            </li>
        )
    }
})

var Comments = React.createClass({
    getInitialState: function() {
        return {
            comments: [],
            quotes: [],
            stream: new Rx.Subject()
        }
    },
    showAnswerForm: function(comment){
        this.state.stream.onNext({action: 'SOME'})
        if(!!comment)
            this.setState({quote_form_for: comment.id})
        else
            this.setState({quote_form_for: null})
    },
    showEditForm: function(comment) {
        this.setState({edit_form_for: comment.id})
    },
    componentWillMount: function(){
        var self = this
        $.getJSON('/comment/'+this.props.entity+'/'+this.props.entity_id+'/json/all', function(res){
            var comments = []
            var quotes = {}
            for(var i in res.data){
                var quote_for = res.data[i].quote_for_id;
                if(!!quote_for){
                    quotes[quote_for] = quotes[quote_for] || []
                    quotes[quote_for].unshift(res.data[i]);
                }else{
                    comments.push(res.data[i])
                }
            }
            self.setState({comments: comments, quotes: quotes})
        });

        commentsStream.filter(function(data) { return data.sender != self && data.entity == self.props.entity && data.entity_id == self.props.entity_id}).subscribe(function(data){
            self.state.stream.onNext(data)
        })

        this.state.stream.subscribe(function(data){
            data.entity = self.props.entity
            data.entity_id = self.props.entity_id
            data.sender = self
            commentsStream.onNext(data)
        })
    },
    render: function() {
        var className = (this.props.className || '') + ' comments'
        var self = this
        return(
            <div>
                <ul className={className}>
                    <CommentForm entity={this.props.entity} entity_id={this.props.entity_id} root={this}/>
                    {this.state.comments.map(function(comment, i) {
                        return <Comment entity={self.props.entity} entity_id={self.props.entity_id} key={'comment'+i} comment={comment} stream={self.state.stream} root={self}/>;
                    })}
                </ul>
            </div>
        )
    }
})

var Quotes = React.createClass({
    render: function() {
        var self = this
        var comments = this.props.comments || []
        return(
            <ul className='quotes'>
                {comments.map(function(comment, i) {
                    return <Comment entity={self.props.entity} entity_id={self.props.entity_id} key={'quote_'+i} comment={comment} stream={self.props.stream} root={self.props.root}/>;
                })}
                {this.props.quoteForm}
            </ul>
        )
    }
})

var Comment = React.createClass({
    getInitialState: function(){
        return {
            'showForm': null
        }
    },
    showQuoteForm: function(e){
        e.preventDefault()
        this.props.stream.onNext({action: 'quote', comment: this})
    },
    showEditForm: function(e){
        e.preventDefault()
        this.props.stream.onNext({action: 'edit', comment: this})
    },
    deleteComment: function(e){
        e.preventDefault()
        var self = this
        Popup.show({
            title: 'Удалить комментарий',
            content: 'Вы уверены,что хотите удалить комментарий?',
            closeButton: false,
            buttons: [
                {
                    name: 'Да',
                    className: 'left',
                    action: function(popup){
                        $.ajax({
                            url: '/comment/'+self.props.comment.id,
                            type: 'DELETE',
                            success: function(res) {
                                var storage = CommentStorageFactory.get(self.props.entity, self.props.entity_id)
                                storage.remove(self.props.comment, res.comment)
                                popup.onClose()
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
    },
    componentWillMount: function(){
        var self = this
        this.props.stream.filter(function(data){ return data.action == 'quote'}).subscribe(function(data){
            if(self.state.showForm) self.setState({showForm: null})
            if(self == data.comment) self.setState({showForm: 'quote'})
        })
        this.props.stream.filter(function(data){ return data.action == 'edit'}).subscribe(function(data){
            if(self.state.showForm) self.setState({showForm: null})
            if(self == data.comment) self.setState({showForm: 'edit'})
        })
    },
    deleteComment: function(e){
        e.preventDefault()
        var self = this
        Popup.show({
            title: 'Удалить комментарий',
            content: 'Вы уверены,что хотите удалить комментарий?',
            closeButton: false,
            buttons: [
                {
                    name: 'Да',
                    className: 'left',
                    action: function(popup){
                        $.ajax({
                            url: '/comment/'+self.props.comment.id,
                            type: 'DELETE',
                            success: function(res) {
                                var storage = CommentStorageFactory.get(self.props.entity, self.props.entity_id)
                                storage.remove(self.props.comment, res.comment)
                                popup.onClose()
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
    },
    componentDidMount: function(){
        $(this.getDOMNode()).find("a.image").fancybox({});
    },
    render: function() {
        var comment = this.props.comment
        var root = this.props.root
        var answerButton = null;
        var deleteButton = null;
        var editButton = null;
        var media = null;
        var quoteForm = null;
        var text = markup(comment.text);

        if(this.state.showForm == 'edit')
            return <CommentForm comment={comment} stream={this.props.stream} root={root}/>

        if(this.state.showForm == 'quote')
            quoteForm =  <CommentForm entity={comment.entity} entity_id={comment.entity_id} quote_for={comment.id} root={root}/>

        if(current_user.is_authorized && comment.status != 'deleted') {
            if(current_user.id != comment.author.id) {
                answerButton = <a href="#"  className="answer-button" onClick={this.showQuoteForm}>Ответить</a>
            } else {
                deleteButton = <a href="#"  className="delete-button" onClick={this.deleteComment}>Удалить</a>
                editButton = <a href="#"  className="edit-button" onClick={this.showEditForm}>Редактировать</a>
            }
        }
        if(comment.files.length){
            media = (
                <div className={"media-holder  count-"+comment.files.length}>
                {comment.files.map(function(file){ return(
                    <div key={"comment_"+comment.id+"_id_"+file.id}  className="media approved">
                        <a href={file.origin}  data-fancybox-group={"comment_"+comment.id} className="image" style={{'backgroundImage': "url('"+file.url+"')"}}></a>
                    </div>
                )})}
                </div>
            )
        }
        if(comment.status == 'deleted') {
            text = '<span class="system-message" >'+comment.text+'</span>'
            media = null
        }
        return(
            <li className="comment">
                <UserIcon user={comment.author}/>
                <div className="message frame">
                    <div className="fa fa-caret-left arrow"></div>
                    <div className="header">
                        <a href={'/user/profile/'+comment.author.id}>{comment.author.full_name}</a>
                        <span className="datetime">{niceDateFormat(comment.datetime)}</span>
                        {deleteButton}
                        {editButton}
                        {answerButton}
                        {deleteButton}
                    </div>
                    <div className="text" dangerouslySetInnerHTML={{__html: text}}></div>
                    {media}
                    <div className="footer"></div>
                </div>
                <Quotes quoteForm={quoteForm} comments={root.state.quotes[comment.id]} entity={this.props.entity} entity_id={this.props.entity_id} stream={this.props.stream} root={root}/>
             </li>
        )
    }
})



$(document).ready(function(){
    $('.comments-counter').each(function(){
        var entity = $(this).attr('data-entity');
        var entity_id = $(this).attr('data-entity-id');
        var count = parseInt($(this).attr('data-count')) || 0;
        React.render( <CommentsCounter entity={entity} entity_id={entity_id} count={count}/>, $(this)[0]);
    });
});
