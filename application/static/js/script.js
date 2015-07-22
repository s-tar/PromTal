var base_url = location.protocol+'//'+location.hostname+(location.port ? ':'+location.port: '');

$( window ).load(function() {
    setTimeout(function(){
        $('textarea.autosize').textareaAutoSize();
        tinymce.init({
            selector:'textarea.editor',
            height : 200,
            plugins : 'code pagebreak image',
            pagebreak_separator: "<!-- page break -->",
            file_picker_callback: function(callback, value, meta) {
                // Provide file and text for the link dialog
                if (meta.filetype == 'file') {
                    callback('mypage.html', {text: 'My text'});
                }

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
                if (meta.filetype == 'media') {
                    callback('movie.mp4', {source2: 'alt.ogg', poster: 'image.jpg'});
                }
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
    }, 100);
});