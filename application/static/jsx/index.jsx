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
