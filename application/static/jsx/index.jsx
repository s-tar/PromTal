React.render(
    <AJAXForm action="/demo_form" method="post" onSuccess={wellDone}>
        <Input type="text" name="first_name"  onChange={someChange}/>
        <div>
            <span><Input type="text" name="last_name"/></span>
        </div>
        <Input type="text" name="email"/>
        <Input type="text" name="email"/>
        <TextArea name="text"></TextArea>
        <Input type="submit" value="Submit"/>
    </AJAXForm>,
    document.getElementById('test_form'))

function someChange(){
    console.log('CHANGE')
}
function wellDone(){
    console.log( 'DONE!')
}
