var MediaUploader = React.createClass({
    getInitialState: function() {
        return {
            opened: false,
            fileUploader: null
        }
    },
    close: function() {
        this.setState({ opened: false, fileUploader: null })
    },
    showUploader: function(type){
        this.setState({fileUploader: type})
    },
    onClick: function(event){
        this.setState({ opened: !this.state.opened, fileUploader: null })
    },
    onInsideClick: function(event){
        event.stopPropagation()
    },
    onOutsideClick: function(){
        if(!this.state.fileUploader)
            this.setState({opened: false})
    },
    componentDidMount: function() {
        window.addEventListener('click', this.onOutsideClick);
    },
    componentWillUnmount: function() {
        window.removeEventListener('click', this.onOutsideClick);
    },
    render: function() {
        var inner;
        var openedClass = this.state.opened ? 'opened' : '';
        if(!this.state.fileUploader)
            inner = <MediaButtons showUploader={this.showUploader}/>
        else
            inner = <FileUploader type={this.state.fileUploader} close={this.close}/>

        return(
            <div className={"media-uploader " + openedClass} onClick={this.onInsideClick}>
                <div className="options">
                    {inner}
                    <div className="arrow fa fa-caret-down"></div>
                </div>
                <button type="button" onClick={this.onClick} className='button icon toggle'><span className="fa fa-paperclip"></span></button>
            </div>
        )
    }
})
var MediaButtons = React.createClass({
    onClick: function(type){
        var self = this
        function wrapper(e){
            self.props.showUploader(type)
        }
        return wrapper
    },
    render: function(){
        return (
            <div className="buttons">
                <button type="button" onClick={this.onClick('image')}><span className="fa fa-picture-o"></span> Картинку</button>
                <button type="button" onClick={this.onClick('video')}><span className="fa fa-film"></span> Видео</button>
                <button type="button" onClick={this.onClick('audio')}><span className="fa fa-music"></span> Аудио</button>
            </div>
        )
    }
})

var FileUploader = React.createClass({
    render: function(){
        var title = 'Загрузка';
        switch(this.props.type) {
            case 'image': title += ' картинки';break;
            case 'video': title += ' видео';break;
            case 'audio': title += ' аудио';break;
        }
        return (
            <div className="file-uploader">
                <h3 className="title">{title}</h3>
                <div className="url-wrapper">
                    <input type="text" name="url" placeholder="Введите адрес"/>
                </div>
                <div className="separator"><span>ИЛИ</span></div>
                <div className="upload-area">
                    <div className="drop-area">Перетащите файл или кликните для загрузки.</div>
                </div>
                <div className="buttons">
                    <button type="button" className="button">Добавить</button>
                    <button type="button" onClick={this.props.close}className="button cancel">Отмена</button>
                </div>
            </div>
        )
    }
})