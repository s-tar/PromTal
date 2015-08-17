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
        tinymce.init({
            selector:'textarea.editor',
            language : "ru",
            height : 300,
            convert_urls: false,
            plugins : [
                "pagebreak",
                "advlist autolink lists link image charmap print preview anchor",
                "searchreplace visualblocks code fullscreen",
                "insertdatetime media table contextmenu paste"
            ],
            statusbar: false,
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


var _MS_PER_DAY = 1000 * 60 * 60 * 24;
function dateDiffInDays(a, b) {
  var utc1 = Date.UTC(a.getFullYear(), a.getMonth(), a.getDate());
  var utc2 = Date.UTC(b.getFullYear(), b.getMonth(), b.getDate());

  return Math.floor((utc2 - utc1) / _MS_PER_DAY);
}
function niceDateFormat(date, time){
    var now = new Date()
    if(!date) return ''
    time = time || true;
    date = new Date(date)
    if(dateDiffInDays(now, date) == 0) return date.format("Сегодня" + (time ? " в HH:MM" : ""));
    if(dateDiffInDays(now, date) == -1) return date.format("Вчера" + (time ? " в HH:MM" : ""));
    if(dateDiffInDays(now, date) == 1) return date.format("Завтра" + (time ? " в HH:MM" : ""));

    return date.format("dd.mm.yy" + (time ? " в HH:MM" : ""));
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
    var ih = image[0].naturalHeight;
    var iw = image[0].naturalWidth;
    if(ih >= h && iw >= w) cls = 'cover'
    media.removeClass('contain').removeClass('cover').addClass(cls);
}

function LazyPaginator ( options ) {
    this.url = options.url || null;
    this.targetElem = $( options.targetElem ) || null;
    this.buttonMore = $( options.buttonMore ) || null;
    this.render = options.render || function () {};
    this.posts = [];
    this.nextPage = 1;
    this.pagesAmount = 0;

    this.init = function () {
        if ( !this.targetElem || !this.buttonMore ) return;

        var that = this;
        this.buttonMore.on("click", function () {
            that.get();
        });
    };

    this.get = function () {

        var that = this;

        $.ajax({
            url: that.url,
            method: "GET",
            data: "page=" + that.nextPage,
            dataType: "json"
        }).done( function ( data ) {
            that.nextPage = data.paginator.page + 1;
            that.pagesAmount = data.paginator.pages;
            that.append( data.objects );

            if ( that.nextPage > that.pagesAmount ) {
                that.buttonMore.hide();
            } else {
                that.buttonMore.show();
            }
        });
    };

    this.append = function ( posts ) {
        posts = (posts instanceof Array) ? posts : [];
        this.posts = this.posts.concat(posts);

        for (var i=0, len = posts.length; i < len; i++) {
            this.targetElem.append( this.render( posts[i] ) );
        }
    };
}


$(document).on('click', '.company-structure .workers-toggle a', function(e){
    e.preventDefault();
    $(this).closest('.workers').toggleClass('show');
})

$(document).on('selectstart', '.company-structure .structure', function(e) {
    e.preventDefault();
});
$(document).ready(function(){
    var structure = $('.company-structure .structure');
    $('.company-structure .structure').removeClass('loading');
    structure.scrollLeft((structure.find('.level-0').outerWidth()-structure.parent().width()) /2);
})
$(document).on('mousedown', '.company-structure .structure', function(e){
    if(event.which == 1) {
        var $this = $(this);
        var start_x = e.clientX - $(this).offset().left;
        var start_y = e.clientY - $(this).offset().top;
        var start_scroll_top = $(document).scrollTop();
        var start_scroll_left = $(this).scrollLeft();
        var timeout = setTimeout(function () {
            $('body').addClass('dragging');
            $this.on('mousemove', function (e) {
                var x = e.clientX - $(this).offset().left;
                var y = e.clientY - $(this).offset().top;
                var delta_x = x - start_x;
                var delta_y = start_y - y;
                $(document).scrollTop(start_scroll_top + delta_y +2);
                $(this).scrollLeft(start_scroll_left - delta_x);

            })

        }, 10);

        $(this).on('mouseup', clear);
        $(window).on('mouseup', clear);
        function clear(e) {
            $('body').removeClass('dragging');
            clearTimeout(timeout);
            $this.off('mouseup mousemove');
        }
    }
})