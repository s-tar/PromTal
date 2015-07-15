React.render(
    <AJAXForm action="/user/login" method="post" className="form-signin" onSuccess={wellDone}>
        <Input className="form-control" type="text" name="login" placeholder="Логин" onChange={someChange}/>
        <Input className="form-control" type="password" name="password" placeholder="Пароль" />
        <Input className="btn btn-lg btn-primary btn-block" type="submit" value="Вход"/>
        <label className="checkbox pull-left">
            <Input type="checkbox" value="remember-me"/>
            Remember me
        </label>
    </AJAXForm>,
    document.getElementById('log_in_form'))


React.render(
    <AJAXForm action="/user/login" method="post" onSuccess={wellDone}>
        <Input type="text" name="login" placeholder="Логин" onChange={someChange}/>
        <Input type="password" name="password" placeholder="Пароль" />
        <Input type="submit" value="Вход"/>
    </AJAXForm>,
    document.getElementById('login_form'))


React.render(
    <AJAXForm action="/user/registration" method="post" onSuccess={wellDone}>
        <Input type="text" name="login" placeholder="Логин" onChange={someChange}/>
        <Input type="password" name="password" placeholder="Пароль" />
        <Input type="password" name="repassword" placeholder="Повтор пароля" />
        <Input type="submit" value="Регистрация"/>
    </AJAXForm>,
    document.getElementById('registration_form'))

function someChange(){
    console.log('CHANGE')
}
function wellDone(){
    console.log( 'DONE!')
}
