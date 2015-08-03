var commentsStream = new Rx.Subject();

var CommentStorageFactory
CommentStorageFactory = (function(){
    var storages = {};

    function CommentStorageFactory(){};

    CommentStorageFactory.get = function (entity, id) {
        var key = entity+'.'+id
        if(!storages[key])
            storages[key] = new CommentStorage(entity, id)

        return storages[key];
    };

    return CommentStorageFactory;
})();

var CommentStorage
CommentStorage = (function(){
    function CommentStorage(entity, entity_id) {
        this.id = Math.random();
        this.entity = entity;
        this.entity_id = entity_id;
        this.comments_count = null;
        this.comments = [];
        this.quotes = [];

        this.loadDataStream = Rx.Observable.just('/comment/'+this.entity+'/'+this.entity_id+'/json/all')
            .flatMap(function(requestUrl) {
                return Rx.Observable.fromPromise(jQuery.getJSON(requestUrl));
            });
    };

    CommentStorage.prototype.updateNotify = function() {
        commentsStream.onNext({action:'update', entity: this.entity, entity_id: this.entity_id});
    }

    CommentStorage.prototype.getCommentsCount = function() {
        return this.comments_count || 0;
    }

    CommentStorage.prototype.load = function () {
        var self = this;
        this.loadDataStream.subscribe(function(response) {
            self.comments = []
            self.quotes = []
            self.comments_count = response.data.length;
            for(var i in response.data){
                var quote_for = response.data[i].quote_for_id;
                if(!!quote_for){
                    self.quotes[quote_for] = self.quotes[quote_for] || []
                    self.quotes[quote_for].unshift(response.data[i]);
                }else{
                    self.comments.push(response.data[i])
                }
            }
            self.updateNotify();
        });
    };

    CommentStorage.prototype.getAll = function () {
        return this.comments || [];
    };

    CommentStorage.prototype.getQuotes = function (comment_id) {
        return this.quotes[comment_id] || [];
    };

    CommentStorage.prototype.get = function (parent_id) {
        return this.comments[parent_id];
    };

    CommentStorage.prototype.addAll = function(comments){
        this.comments = comments;
    };

    CommentStorage.prototype.add = function(comment){
        var qid = comment.quote_for_id;
        if(!qid){
            this.comments.unshift(comment)
        }else{
            this.quotes[qid] = this.quotes[qid] || []
            this.quotes[qid].push(comment)
        }
        this.comments_count++;
        this.updateNotify();
    };

    return CommentStorage;
})();

var CommentsCounter = React.createClass({
    getInitialState: function() {
        return {count: this.props.count || 0}
    },
    componentWillMount: function(){
        var self = this
        var entity = this.props.entity
        var entity_id = this.props.entity_id
        var storage = CommentStorageFactory.get(entity, entity_id)

        if(!storage.comments_count)storage.comments_count = this.props.count
        commentsStream.filter(function(data){ return data.action == 'update' &&
                data.entity == entity &&
                data.entity_id == entity_id })
            .subscribe(function(data){
                self.setState({count: storage.getCommentsCount()});
        })
    },
    render: function() {
        return(
            <div><span className="fa fa-comments-o"></span>{this.state.count}</div>
        )
    }
})
var NewComment = React.createClass({
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
    updateSubmitDisabled: function(data){
        this.setState({disabled: this.refs.mediaHolder.state.count == 0 && !this.state.text})
    },
    componentDidMount: function(){
        var self = this
        this.state.stream
            .filter(function(data){ return data.action == 'updateSubmitDisabled' && self.isMounted()})
            .subscribe(self.updateSubmitDisabled)
    },
    render: function() {
        if(!current_user.is_authorized) return(false)
        if(!!(this.props.entity && this.props.entity_id) || !!this.props.quote_for)

        var action = '/comment/new'
        if(!!this.props.quote_for)
            action = '/comment/quote/new'
        return(
            <ul className="comments new">
                <li className="comment">
                    <UserIcon user={current_user}/>
                    <div className="message frame">
                        <div className="fa fa-caret-left arrow"></div>
                        <div className="text">
                            <AJAXForm ref='form' className="custom-form" action={action} method="post" onSuccess={this.onSuccess}>
                                <div className="wrapper">
                                    <input type="hidden" name="entity_name" value={this.props.entity}/>
                                    <input type="hidden" name="entity_id" value={this.props.entity_id}/>
                                    <input type="hidden" name="quote_for" value={this.props.quote_for}/>
                                    <TextArea ref="comment" focus={!!this.props.quote_for} name="comment" autosize={true} onKeyDown={this.onKeyDown} onChange={this.onChange} placeholder="Оставить комментарий" value={this.state.text}></TextArea>
                                    <div className="right-buttons">
                                        <MediaUploader stream={this.state.stream} holder={this}/>
                                        <button type="submit" disabled={this.state.disabled} className="button send" title="Отправить"><span className="fa fa-send"></span></button>
                                    </div>
                                    <MediaHolder ref="mediaHolder" stream={this.state.stream} holder={this}/>
                                </div>
                            </AJAXForm>
                        </div>
                    </div>
                </li>
            </ul>
        )
        return(false)
    }
})

var Comments = React.createClass({
    getInitialState: function() {
        return {
            comments: [],
            quote_form_for: null
        }
    },
    showAnswerForm: function(comment){
        if(!!comment)
            this.setState({quote_form_for: comment.id})
        else
            this.setState({quote_form_for: null})
    },
    componentWillMount: function(){
        var self = this
        var entity = this.props.entity
        var entity_id = this.props.entity_id
        var storage = CommentStorageFactory.get(entity, entity_id)
        storage.load();
        commentsStream.filter(function(data){ return data.action == 'update' &&
                data.entity == entity &&
                data.entity_id == entity_id })
            .subscribe(function(data){
                self.setState({comments: storage.getAll()});
        })
        self.setState({comments: storage.getAll()});
    },
    render: function() {
        var className = (this.props.className || '') + ' comments'
        var self = this
        return(
            <div>
                <NewComment entity={this.props.entity} entity_id={this.props.entity_id} root={this}/>
                <ul className={className}>
                    {this.state.comments.map(function(comment, i) {
                        return <Comment key={'comment'+i} comment={comment} root={self}/>;
                    })}
                </ul>
            </div>
        )
    }
})

var Quotes = React.createClass({
    render: function() {
        var self = this
        return(
            <ul className='quotes'>
                {this.props.comments.map(function(comment, i) {
                    return <Comment key={'quote_'+i} comment={comment} root={self.props.root}/>;
                })}
            </ul>
        )
    }
})

var Comment = React.createClass({
    getInitialState: function(){
        return {'showQuoteForm': false }
    },
    showQuoteForm: function(e){
        e.preventDefault()
        this.props.root.showAnswerForm(this.props.comment)
    },
    componentDidMount: function(){
        console.log($(this.getDOMNode()).find("a.image").length)
        $(this.getDOMNode()).find("a.image").fancybox({});
    },
    render: function() {
        var comment = this.props.comment
        var storage = CommentStorageFactory.get(comment.entity, comment.entity_id)
        var quoteForm = this.props.root.state.quote_form_for == comment.id ?
            <NewComment entity={comment.entity} entity_id={comment.entity_id} quote_for={comment.id} root={this.props.root}/> : ''

        var answerButton = current_user.is_authorized ?
            <a href="#"  className="answer-button" onClick={this.showQuoteForm}>Ответить</a> : ''
        var media = ''
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

        return(
            <li className="comment">
                <UserIcon user={comment.author}/>
                <div className="message frame">
                    <div className="fa fa-caret-left arrow"></div>
                    <div className="header">
                        <a href={'/user/profile/'+comment.author.id}>{comment.author.full_name}</a>
                        <span className="datetime">{niceDateFormat(comment.datetime)}</span>
                        {answerButton}
                    </div>
                    <div className="text" dangerouslySetInnerHTML={{__html: markup(comment.text)}}></div>
                    {media}
                    <div className="footer"></div>
                </div>
                <Quotes comments={storage.getQuotes(comment.id)} root={this.props.root}/>
                {quoteForm}
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
