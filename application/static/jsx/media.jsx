var MediaUploader = React.createClass({
    getInitialState: function() {
        return { content: null }
    },
    close: function() {
        this.props.holder.setState({disabled: false})
        this.setState({ content: null })
    },
    showUploader: function(type){
        this.props.holder.setState({disabled: true})
        this.setState({content: <FileUploader stream={this.props.stream} holder={this.props.holder} type={type} close={this.close}/>})
    },
    onClick: function(event){
        if(!this.state.content)
            this.setState({content: <SelectMediaButtons showUploader={this.showUploader}/>})
        else if(React.addons.TestUtils.isElementOfType(this.state.content, SelectMediaButtons))
            this.setState({content: null})
    },
    onInsideClick: function(event){
        event.stopPropagation()
    },
    onOutsideClick: function(){
        if(React.addons.TestUtils.isElementOfType(this.state.content, SelectMediaButtons))
            this.close()
    },
    componentDidMount: function() {
        window.addEventListener('click', this.onOutsideClick);
    },
    componentWillUnmount: function() {
        window.removeEventListener('click', this.onOutsideClick);
    },
    render: function()  {
        return(
            <div className={"media-uploader " + (!this.state.content ? '' : 'opened')} onClick={this.onInsideClick}>
                <div className="options">
                    {this.state.content}
                    <div className="arrow fa fa-caret-down"></div>
                </div>
                <button type="button" onClick={this.onClick} className='button icon toggle'><span className="fa fa-paperclip"></span></button>
            </div>
        )
    }
})

var SelectMediaButtons = React.createClass({
    onClick: function(type){
        var self = this
        return function(e){ self.props.showUploader(type) }
    },
    render: function(){
        return (
            <div className="buttons">
                <button type="button" onClick={this.onClick('image')}><span className="fa fa-picture-o"></span> Картинку</button>
                <button type="button" onClick={this.onClick('video')}><span className="fa fa-film"></span> Видео</button>
            </div>
        )
    }
})


var Media = React.createClass({
    getInitialState: function(){
        return {src: null, status: 'active', fromFile: null, url: null}
    },
    cancel: function(){
        var count = this.props.holder.state.count
        this.props.holder.setState({count: count-1})
        this.setState({status: 'canceled'})
    },
    approve: function(){
        var count = this.props.holder.state.count
        this.props.holder.setState({count: count+1})
        this.setState({status: 'approved'})
    },
    onInputFileChange: function(){
        var self = this
        var input = this.refs.fileInput.getDOMNode()
        if (input.files && input.files[0]) {
            var reader = new FileReader();
            reader.onload = function (e) {
                self.setState({src: e.target.result, url: null});
                self.props.stream.onNext({
                    action: 'updatePreview',
                    src: e.target.result,
                    filename: input.value.split('\\').pop()});
            }
            reader.readAsDataURL(input.files[0]);
        }

    },
    componentWillMount: function(){
        var self = this
        var activeStream = this.props.stream.filter(function(){ return self.state.status == 'active' })
        activeStream.filter(function(data){ return data.action == 'selectMediaFile'})
            .subscribe(function(){
                self.refs.fileInput.getDOMNode().click();
            })
        activeStream.filter(function(data){ return data.action == 'selectMediaUrl'})
            .subscribe(function(data){
                self.props.stream.onNext({action: 'updatePreview', src: data.url});
                self.refs.fileInput.getDOMNode().value = ''
                self.setState({src: null, url: data.url})
            })
        activeStream.filter(function(data){ return data.action == 'mediaApprove' })
            .subscribe(function(){
                self.approve()
        })
        activeStream.filter(function(data){ return data.action == 'mediaCancel'})
            .subscribe(function(){
                self.cancel()
        })
    },
    render: function(){
        var src = this.state.url || this.state.src
        var image = !src ? '' : <div className="image" style={{'backgroundImage': "url('"+src+"')"}}></div>
        var urlInput = <input type="text" name="file" value={this.state.url}/>
        var fileInput = <input ref="fileInput"  type="file" name="file" onChange={this.onInputFileChange}/>
        if(this.state.status == 'approved') {
            urlInput = !this.state.url ? '' : urlInput
            fileInput = !this.state.src ? '' : fileInput
        }
        if(this.state.status == 'canceled')
            return null
        else
            return (
                <div className={"media "+this.state.status}>
                    <button className="cancel" onClick={this.cancel}><span className="fa fa-times"></span></button>
                    {image}
                    {urlInput}
                    {fileInput}
                </div>
            )

    }
})

var MediaHolder = React.createClass({
    getInitialState: function(){
        return {media: [], key: 0, count: 0}
    },
    createMedia: function() {
        var key = this.state.key + 1;
        var media = this.state.media;
        media.push(<Media holder={this} key={"media_"+key} stream={this.props.stream}/>)
        this.setState({media: media, key: key})
    },
    componentWillMount: function(){
        var self = this
        this.props.stream
            .filter(function(data){ return data.action == 'createMedia'})
            .subscribe(function(){
                self.createMedia()
        });
    },
    render:function(){
        return(
            <div className={"media-holder"  + " count-" + this.state.count}>
                {this.state.media.map(function(media){ return media })}
            </div>
        )
    }
})

var FileUploader = React.createClass({
    getInitialState: function() {
        return { inputChangeStream: new Rx.Subject(), preview: null }
    },
    onCancel: function(){
        this.props.stream.onNext({action: 'mediaCancel'});
        this.props.close()
    },
    onApprove: function(){
        this.props.stream.onNext({action: 'mediaApprove'});
        this.props.close()
    },
    onUploadClick: function(){
        this.props.stream.onNext({action: 'selectMediaFile'});
    },
    onUrlChange: function(e){
        this.state.inputChangeStream.onNext(e.target.value)
    },
    urlChangeHandler: function(url){
        this.props.stream.onNext({action: 'selectMediaUrl', url: url});
    },

    getTitle: function() {
        var title = 'Загрузка';
        switch(this.props.type) {
            case 'image': title += ' картинки';break;
            case 'video': title += ' видео';break;
            case 'audio': title += ' аудио';break;
        }
        return title
    },
    updatePreview: function(data){
        this.setState({preview: data.src })
        this.refs.urlField.getDOMNode().value = data.filename || data.src
    },

    componentDidMount: function(){
        var self = this
        this.state.inputChangeStream.debounce(500).subscribe(this.urlChangeHandler)
        this.props.stream.onNext({action: 'createMedia'});
        this.props.stream
            .filter(function(data){ return data.action == 'updatePreview' && self.isMounted()})
            .subscribe(self.updatePreview)
    },
    render: function() {
        var preview = !this.state.preview ? '' : <img src={this.state.preview} alt=''/>
        return (
            <div className="file-uploader">
                <h3 className="title">{this.getTitle()}</h3>
                <div className="preview">{preview}</div>
                <div className="url-wrapper">
                    <input type="text" ref="urlField" name="url" placeholder="Введите адрес" onChange={this.onUrlChange}/>
                    <button type="button" onClick={this.onUploadClick} className="button download">
                        <span className="fa fa-download"></span>
                    </button>
                </div>
                <div className="buttons">
                    <button type="button" className="button" onClick={this.onApprove}>Добавить</button>
                    <button type="button" onClick={this.onCancel} className="button cancel">Отмена</button>
                </div>
            </div>
        )
    }
})