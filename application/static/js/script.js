var base_url = location.protocol+'//'+location.hostname+(location.port ? ':'+location.port: '');

function locationReload(){
    window.location.reload();
}

String.prototype.format = String.prototype.f = function(){
    var args = arguments;
    return this.replace(/\{(\d+)\}/g, function(m,n){
        return args[n] ? args[n] : m;
    });
};

$( window ).load(function() {
    setTimeout(function(){
        $('textarea.autosize').textareaAutoSize();
        tinymce.init({
            selector:'textarea.editor',
            language : "ru",
            height : 200,
            plugins : [
                "pagebreak",
                "advlist autolink lists link image charmap print preview anchor",
                "searchreplace visualblocks code fullscreen",
                "insertdatetime media table contextmenu paste"
            ],
            pagebreak_separator: "<!-- page break -->",
            file_picker_callback: function(callback, value, meta) {
                // Provide file and text for the link dialog
                //if (meta.filetype == 'file') {
                //    callback('mypage.html', {text: 'My text'});
                //}

                // Provide image and alt text for the image dialog
                if (meta.filetype == 'image') {
                    var form = $('<form id="file_upload_form" action="/file/upload/image" style="display: none" method="post" enctype="multipart/form-data"></form>');
                    var input = $('<input type="file" name="file" />');
                    form.append(input);
                    $('body').append(form);
                    input.on('change', function(){form.submit()});
                    form.submit(function (event) {
                        event.preventDefault();
                        var formData = new FormData($('#file_upload_form')[0]);
                        $.ajax({
                            url: $(this).attr('action'),
                            type: $(this).attr('method'),
                            data: formData,
                            cache: false,
                            contentType: false,
                            processData: false,
                            success: function (res) {
                                form.remove();
                                callback(res.file.url);
                            },
                            error: function(){
                                alert("error in ajax form submission");
                            }
                        });

                        return false;
                    });
                    input.trigger('click');
                }

                // Provide alternative source and posted for the media dialog
                //if (meta.filetype == 'media') {
                //    callback('movie.mp4', {source2: 'alt.ogg', poster: 'image.jpg'});
                //}
            },
            setup : function(editor) {
                editor.on('init', function() {
                    this.getDoc().body.style.fontSize = '12px';
                });
                editor.on('change', function () {
                    tinymce.triggerSave();
                });
            }

        });
    }, 400);
});


function niceDateFormat(date){
    if(!date) return ''
    var now = new Date()
    date = new Date(date)
    if(date.getFullYear() == now.getFullYear() && date.getMonth() == now.getMonth()) {
        if(date.getDate() == now.getDate()) return date.format("Сегодня в HH:MM");
        if(date.getDate() == now.getDate()-1) return date.format("Вчера в HH:MM");
    }
    return date.format("dd.mm.yy в HH:MM");
}

$(window).resize(function(){
    $('.media-holder .approved img').each(function(){
        mediaFill($(this));
    });
});
$(window).load(function(){$(window).trigger('resize')})

function mediaFill(img) {
    var image = $(img);
    var media = $(img).closest('.media');
    var cls = 'contain';
    var h = media[0].offsetHeight;
    var w = media[0].offsetWidth;
    var ih = image[0].offsetHeight;
    var iw = image[0].offsetWidth;

    if(ih >= h && iw >= w) cls = 'cover'
    media.removeClass('contain').removeClass('cover').addClass(cls);
}