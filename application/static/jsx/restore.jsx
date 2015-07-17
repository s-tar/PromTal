React.render(
    <AJAXForm action="/user/restore" method="post" className="form-signin" onSuccess={wellDone}>
        <Input className="form-control" type="text" name="email" placeholder="Email" onChange={someChange}/>
        <Input className="btn btn-lg btn-primary btn-block" type="submit" value="Restore"/>
    </AJAXForm>,
    document.getElementById('restore_form'))

function someChange(){
    console.log('CHANGE')
}
function wellDone(){
    console.log( 'DONE!')
}
