var news = {}
news.delete = function(id) {
    Popup.show({
        title: 'Удалить новость',
        content: 'Вы уверены,что хотите удалить новость?',
        closeButton: false,
        buttons: [
            {
                name: 'Да',
                className: 'left',
                action: function(popup){
                    $.ajax({
                        url: '/news/'+id,
                        type: 'DELETE',
                        success: function() {
                            window.location.href = '/';
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
}