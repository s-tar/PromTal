var user = {}

user.delete = function(id) {
    Popup.show({
        content: 'Вы уверены, что хотите удалить пользователя?',
        closeButton: false,
        buttons: [
            {
                name: 'Да',
                className: 'left',
                action: function(popup){
                    $.ajax({
                        url: '/api/v1/users/'+id+'/',
                        type: 'DELETE',
                        success: function() {
                            window.location.href = '/admin/s_users';
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

user.activate = function(id) {
    Popup.show({
        content: 'Активировать пользователя?',
        closeButton: false,
        buttons: [
            {
                name: 'Да',
                className: 'left',
                action: function(popup){
                    $.ajax({
                        url: '/api/v1/user/activate/'+id+'/',
                        type: 'PUT',
                        success: function() {
                            window.location.href = '/admin/s_users';
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
