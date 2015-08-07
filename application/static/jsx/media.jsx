var MediaUploader = React.createClass({
    getInitialState: function() {
        return { content: null, opened: false }
    },
    close: function() {
        this.state.opened = false
        this.setState({ content: null, opened: this.state.opened })
        this.props.stream.onNext({action: 'updateSubmitDisabled'});
    },
    showUploader: function(type){
        this.state.opened = true
        this.setState({opened: this.state.opened, content: <FileUploader stream={this.props.stream} holder={this.props.holder} type={type} close={this.close}/>})
        this.props.stream.onNext({action: 'updateSubmitDisabled'});
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
        return {id: null, file: this.props.file, src: null, status: 'active', fromFile: null, url: null}
    },
    cancel: function(){
        if(this.state.status == 'approved') {
            this.props.holder.state.count -= 1
            this.props.holder.setState({count: this.props.holder.state.count})
        }
        this.state.status = this.state.file ? 'deleted' : 'canceled';
        this.setState({status: this.state.status})
        this.props.stream.onNext({action: 'updateSubmitDisabled'});
    },
    approve: function(){
        this.props.holder.state.count++
        this.props.holder.setState({count: this.props.holder.state.count})
        this.state.status = 'approved'
        this.setState({status: this.state.status})
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
    onImageLoad: function(e){
        mediaFill(e.target)
    },
    componentDidMount: function(){
        $(window).trigger('resize');
    },
    componentDidUpdate: function(){
       if(this.refs.mediaImage) mediaFill(this.refs.mediaImage.getDOMNode());
    },
    componentWillMount: function(){
        var self = this
        var activeStream = this.props.stream.filter(function(){ return self.state.status == 'active' })
        if(this.state.file) {
            this.state.id = this.state.file.id;
            this.state.url = this.state.file.url;
            this.state.status = 'approved';
        }
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
        var image = !src ? '' : <div className="image"><img ref="mediaImage" src={src} alt="" onLoad={this.onImageLoad}/></div>
        var url_input = <input type="hidden" name="url" value={this.state.url}/>
        var type_input = <input type="hidden" name="file.type" value={this.props.type}/>
        var file_input = <input ref="fileInput"  type="file" name="upload" onChange={this.onInputFileChange}/>
        if(this.state.status == 'approved') {
            file_input = !this.state.src ? '' : file_input
        }else if(this.state.status == 'deleted') {
            file_input = ''
        }
        if(this.state.status == 'canceled')
            return null
        else {
            var inner = (
                <div>
                    <button type="button" className="cancel" onClick={this.cancel}>
                        <span className="fa fa-times"></span>
                    </button>
                    <input type="hidden" name="file.id" value={this.state.id}/>
                    <input type="hidden" name="file.status" value={this.state.status}/>
                    {image}
                    {type_input}
                    {url_input}
                    {file_input}
                </div>
            )

            if(this.state.status == 'approved' || this.state.status == 'active'){
                return <div className={"media " + this.state.status}  style={!src ? {} : {backgroundImage: 'url("'+src+'")'}}>{inner}</div>
            }else{
                return <span className={"media " + this.state.status}>{inner}</span>
            }
        }
    }
})

var MediaHolder = React.createClass({
    getDefaultProps: function(){
        return { files: []}
    },
    getInitialState: function(){
        return {media: [], key: 0, count: 0}
    },
    createMedia: function(type, file) {
        this.state.key += 1;
        var media = this.state.media;
        media.push(<Media holder={this} key={"media_"+this.state.key} type={type} file={file} stream={this.props.stream}/>)
        this.setState({media: this.state.media, key: this.state.key})
    },

    componentWillMount: function(){
        var self = this
        self.props.files.map(function(file){
            self.createMedia(file.type, file);
            self.state.count++;
        });

        this.props.stream
            .filter(function(data){ return data.action == 'createMedia'})
            .subscribe(function(data){
                self.createMedia(data.type)
        });
        this.props.stream
            .filter(function(data){ return data.action == 'clearMedia'})
            .subscribe(function(){
                if(self.isMounted()) self.setState({media: [], key: 0, count: 0})
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
        return { inputChangeStream: new Rx.Subject(), preview: null, disabled: true }
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
        this.setState({'disabled': true})
        this.props.stream.onNext({action: 'selectMediaFile'});
    },
    onUrlChange: function(e){
        this.setState({'disabled': true})
        this.state.inputChangeStream.onNext(e.target.value)
    },
    urlChangeHandler: function(url){
        this.props.stream.onNext({action: 'selectMediaUrl', url: url});
    },
    onImageLoad: function(){
        this.setState({'disabled': false})
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
        this.props.stream.onNext({action: 'createMedia', type: this.props.type});
        this.props.stream
            .filter(function(data){ return data.action == 'updatePreview' && self.isMounted()})
            .subscribe(self.updatePreview)
    },

    render: function() {
        var preview = !this.state.preview ? '' : <div className="wrapper"><img src={this.state.preview} onLoad={this.onImageLoad} alt=''/></div>
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
                    <button type="button" disabled={this.state.disabled} className="button" onClick={this.onApprove}>Добавить</button>
                    <button type="button" onClick={this.onCancel} className="button cancel">Отмена</button>
                </div>
            </div>
        )
    }
})