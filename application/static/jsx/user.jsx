var UserIcon = React.createClass({
    render: function() {
        var user = this.props.user
        var photo = !!user.photo_s ? {'background-image': "url("+user.photo_s+")"} : {}

        function goto_profile(){
            window.location.href='/user/profile/'+ user.id
        }
        return(
           <div className="user-icon" onClick={goto_profile} style={photo} title={user.full_name}></div>
        )
    }
})