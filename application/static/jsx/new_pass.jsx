React.render(
    <AJAXForm action="/user/new_pass" method="post" className="form-signin" onSuccess={wellDone}>
        <Input className="form-control" type="password" name="password_1" placeholder="Пароль" />
        <Input className="form-control" type="password" name="password_2" placeholder="Повторить пароль" />
        <Input className="btn btn-lg btn-primary btn-block" type="submit" value="Сменить"/>
    </AJAXForm>,
    document.getElementById('new_pass_form'))

function wellDone(){
    window.location.href = "/message/Вы сменили пароль";
}
