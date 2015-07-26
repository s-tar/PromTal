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
        commentsStream.subscribe(function(data){
            if( data.action == 'update' && data.entity == entity && data.entity_id == entity_id ) {
                self.setState({count: storage.getCommentsCount()});
            }
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
        return {text: ''}
    },
    onSuccess: function(data){
        var storage = CommentStorageFactory.get(this.props.entity, this.props.entity_id)
        this.setState({text: ''})
        storage.add(data.comment)
    },
    onChange: function(e){
        this.setState({text: e.target.value})
    },
    render: function() {
        return(
            <AJAXForm className="custom-form" action="/comment/new" method="post" onSuccess={this.onSuccess}>
                <div className="wrapper">
                    <input type="hidden" name="entity_name" value={this.props.entity}/>
                    <input type="hidden" name="entity_id" value={this.props.entity_id}/>
                    <input type="hidden" name="quote_for" value={this.props.quote_for}/>
                    <TextArea name="comment" autosize={true} onChange={this.onChange} placeholder="Оставить комментарий" value={this.state.text}></TextArea>
                    <button type="submit" className="button send" title="Отправить"><span className="fa fa-send"></span></button>
                </div>
            </AJAXForm>
        )
    }
})

var Comments = React.createClass({
    getInitialState: function() {
        return {comments: []}
    },
    componentWillMount: function(){
        var self = this
        var entity = this.props.entity
        var entity_id = this.props.entity_id
        var storage = CommentStorageFactory.get(entity, entity_id)
        storage.load();
        commentsStream.subscribe(function(data){
            if( data.action == 'update' && data.entity == entity && data.entity_id == entity_id ) {
                self.setState({comments: storage.getAll()});
            }
        })
        self.setState({comments: storage.getAll()});
    },
    render: function() {
        var className = (this.props.className || '') + ' comments'
        return(
            <ul className={className}>
                {this.state.comments.map(function(comment) {
                    return <Comment comment={comment}/>;
                })}
            </ul>
        )
    }
})

var Quotes = React.createClass({
    render: function() {
        return(
            <ul className='quotes'>
                {this.props.comments.map(function(comment) {
                    return <Comment comment={comment}/>;
                })}
            </ul>
        )
    }
})

var Comment = React.createClass({
    render: function() {
        var comment = this.props.comment
        var storage = CommentStorageFactory.get(comment.entity, comment.entity_id)
        return(
            <li className="comment">
                <UserIcon user={comment.author}/>
                <div className="message frame">
                    <div className="fa fa-caret-left arrow"></div>
                    <div className="header">
                        <a href='/user/profile/{comment.author.id}'>{comment.author.full_name}</a>
                        <span className="datetime">{niceDateFormat(comment.datetime)}</span>
                    </div>
                    <div className="text">{comment.text}</div>
                    <div className="footer"></div>
                </div>
                <Quotes comments={storage.getQuotes(comment.id)}/>
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
