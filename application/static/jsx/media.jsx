var MediaUploader = React.createClass({
    getInitialState: function() {
        return { content: null, media: []}
    },
    close: function() {
        this.props.holder.setState({disabled: false, currentMedia: null})
        this.setState({ content: null })
    },
    showUploader: function(type){
        this.props.holder.setState({disabled: true})
        this.setState({content: <FileUploader holder={this.props.holder} type={type} close={this.close}/>})
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
        this.props.holder.state.stream.subscribe(function(){
            console.log('!!!!!')
        })
        window.addEventListener('click', this.onOutsideClick);
    },
    componentWillUnmount: function() {
        window.removeEventListener('click', this.onOutsideClick);
    },
    render: function() {
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


var UploadPreview = React.createClass({
    getDefaultProps:function(){
        return { url: null }
    },
    getInitialState:function(){
        return { src: null, field: null, approved: true }
    },
    onInputFileChange: function(){
        var self = this
        var input = this.refs.fileInput.getDOMNode()
        this.props.urlField.getDOMNode().value = input.value.split('\\').pop()
        if (input.files && input.files[0]) {
            var reader = new FileReader();
            reader.onload = function (e) {
                self.setState({src: e.target.result});
            }
            reader.readAsDataURL(input.files[0]);
        }

    },
    //componentWillMount: function(){
    //
    //},
    //componentWillUpdate: function() {
    //    if(!!this.props.url) this.state.src = this.props.url
    //},
    componentDidMount: function() {
        if(!this.props.url)
            this.refs.fileInput.getDOMNode().click();
    },
    //componentDidUpdate:  function() {
    //    this.componentDidMount();
    //},
    render: function(){
        var src = this.props.url || this.state.src
        var image = !src ? '' : <img src={src} alt=''/>
        var input = !this.props.url ?
            <input ref="fileInput"  type="file" name="file" onChange={this.onInputFileChange}/> :
            <input type="hidden" name="file" value={input}/>
        if(this.state.approved)
            return (
                <div className="preview">
                    {input}
                    {image}
                </div>
            )
        else
            return null
    }
})

var MediaHolder = React.createClass({
    getInitialState: function(){
        return {}
    },
    render:function(){
        <div className="media-holder"></div>
    }
})

var FileUploader = React.createClass({
    getInitialState: function() {
        return {
            file: null,
            inputChangeStream: new Rx.Subject()
        }
    },
    onUploadClick: function(){
        this.props.holder.state.stream.onNext('asfasf')
        var currentMedia = this.props.holder.state.currentMedia
        var media = this.props.holder.state.media
        if(!currentMedia) {
            currentMedia = <UploadPreview holder={this.props.holder} urlField={this.refs.urlField} type={this.props.type}/>
            media.push(currentMedia)
            this.props.holder.setState({ currentMedia: currentMedia, media: media})
        }
        //

        //this.setState({file: <UploadPreview storage={this.props.storage} urlField={this.refs.urlField} type={this.props.type}/>})
    },
    onUrlChange: function(e){
        this.state.inputChangeStream.onNext(e.target.value)
    },
    urlChangeHandler: function(url){
        this.props.storage.addMedia(url)
        //this.setState({file: <UploadPreview storage={this.props.storage} url={val} urlField={this.refs.urlField} type={this.props.type}/>})
    },
    addFile: function(){

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
    componentDidMount: function(){
        this.state.inputChangeStream.debounce(500).subscribe(this.urlChangeHandler)
    },
    render: function() {
        var preview = !this.state.file ? '' : this.state.file
        return (
            <div className="file-uploader">
                <h3 className="title">{this.getTitle()}</h3>
                {preview}
                <div className="url-wrapper">
                    <input type="text" ref="urlField" name="url" placeholder="Введите адрес" onChange={this.onUrlChange}/>
                    <button type="button" onClick={this.onUploadClick} className="button download"><span className="fa fa-download"></span></button>
                </div>
                <div className="buttons">
                    <button type="button" className="button" onClick={this.addFile}>Добавить</button>
                    <button type="button" onClick={this.props.close} className="button cancel">Отмена</button>
                </div>
            </div>
        )
    }
})