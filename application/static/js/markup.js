var smiles = {
    "/static/images/smiles/tango/smile.png": [":-)", ":)"],
    "/static/images/smiles/tango/laugh.png": [":-D", ":d", ":D", ":-d"],
    "/static/images/smiles/tango/tongue.png": [":-P", ":p", ":P", ":-p"],
    "/static/images/smiles/tango/wink.png": [";-)", ";)"],
    "/static/images/smiles/tango/sad.png": [":-(", ":("],
    "/static/images/smiles/tango/confused.png": [":-S", ":s", ":-s", ":S"],
    "/static/images/smiles/tango/neutral.png": [":-|", ":|"],
    "/static/images/smiles/tango/crying.png": [":'("],
    "/static/images/smiles/tango/embarrassed.png": [":-$", ":$"],
    "/static/images/smiles/tango/glasses-cool.png": ["(H)", "(h)"],
    "/static/images/smiles/tango/angry.png": [":-@", ":@"],
    "/static/images/smiles/tango/angel.png": ["(A)", "(a)"],
    "/static/images/smiles/tango/devil.png": ["(6)"],
    "/static/images/smiles/tango/quiet.png": [":-#", ":#"],
    "/static/images/smiles/tango/teeth.png": ["8o|"],
    "/static/images/smiles/tango/glasses-nerdy.png": ["8-|"],
    "/static/images/smiles/tango/sarcastic.png": ["^o)"],
    "/static/images/smiles/tango/secret.png": [":-*"],
    "/static/images/smiles/tango/sick.png": ["+o("],
    "/static/images/smiles/tango/dont-know.png": [":^)"],
    "/static/images/smiles/tango/thinking.png": ["*-)"],
    "/static/images/smiles/tango/party.png": ["<:o)"],
    "/static/images/smiles/tango/eyeroll.png": ["8-)"],
    "/static/images/smiles/tango/sleepy.png": ["|-)"],
    "/static/images/smiles/tango/coffee.png": ["(C)", "(c)"],
    "/static/images/smiles/tango/good.png": ["(Y)", "(y)"],
    "/static/images/smiles/tango/bad.png": ["(N)", "(n)"],
    "/static/images/smiles/tango/beer.png": ["(B)", "(b)"],
    "/static/images/smiles/tango/drink.png": ["(D)", "(d)"],
    "/static/images/smiles/tango/girl.png": ["(X)", "(x)"],
    "/static/images/smiles/tango/boy.png": ["(Z)", "(z)"],
    "/static/images/smiles/tango/hug-left.png": ["({)"],
    "/static/images/smiles/tango/hug-right.png": ["(})"],
    "/static/images/smiles/tango/vampire.png": [":-[", ":["],
    "/static/images/smiles/tango/cake.png": ["(^)"],
    "/static/images/smiles/tango/love.png": ["(L)", "(l)"],
    "/static/images/smiles/tango/love-over.png": ["(U)", "(u)"],
    "/static/images/smiles/tango/kiss.png": ["(K)", "(k)"],
    "/static/images/smiles/tango/present.png": ["(G)", "(g)"],
    "/static/images/smiles/tango/rose.png": ["(F)", "(f)"],
    "/static/images/smiles/tango/rose-dead.png": ["(W)", "(w)"],
    "/static/images/smiles/tango/camera.png": ["(P)", "(p)"],
    "/static/images/smiles/tango/film.png": ["(~)"],
    "/static/images/smiles/tango/cat.png": ["(@)"],
    "/static/images/smiles/tango/dog.png": ["(&)"],
    "/static/images/smiles/tango/phone.png": ["(T)", "(t)"],
    "/static/images/smiles/tango/mobile.png": ["(mp)"],
    "/static/images/smiles/tango/lamp.png": ["(I)", "(i)"],
    "/static/images/smiles/tango/musical-note.png": ["(8)"],
    "/static/images/smiles/tango/moon.png": ["(S)"],
    "/static/images/smiles/tango/star.png": ["(*)"],
    "/static/images/smiles/tango/mail.png": ["(E)", "(e)"],
    "/static/images/smiles/tango/clock.png": ["(O)", "(o)"],
    "/static/images/smiles/tango/msn.png": ["(M)", "(m)"],
    "/static/images/smiles/tango/snail.png": ["(sn)"],
    "/static/images/smiles/tango/turtle.png": ["(tu)"],
    "/static/images/smiles/tango/sheep.png": ["(bah)"],
    "/static/images/smiles/tango/plate.png": ["(pl)"],
    "/static/images/smiles/tango/bowl.png": ["(||)"],
    "/static/images/smiles/tango/pizza.png": ["(pi)"],
    "/static/images/smiles/tango/soccerball.png": ["(so)"],
    "/static/images/smiles/tango/car.png": ["(au)"],
    "/static/images/smiles/tango/airplane.png": ["(ap)"],
    "/static/images/smiles/tango/umbrella.png": ["(um)"],
    "/static/images/smiles/tango/island.png": ["(ip)"],
    "/static/images/smiles/tango/rain.png": ["(st)"],
    "/static/images/smiles/tango/thunder.png": ["(li)"],
    "/static/images/smiles/tango/coins.png": ["(mo)"],
    "/static/images/smiles/tango/computer.png": ["(co)"],
    "/static/images/smiles/tango/console.png": ["(xx)"],
    "/static/images/smiles/tango/question.png": ["(?)"],
    "/static/images/smiles/tango/brb.png": ["(brb)"],
    "/static/images/smiles/tango/cigarette.png": ["(ci)"],
    "/static/images/smiles/tango/handcuffs.png": ["(%)"],
    "/static/images/smiles/tango/highfive.png": ["(h5)"],
    "/static/images/smiles/tango/fingers-crossed.png": ["(yn)"],
    "/static/images/smiles/tango/foot-in-mouth.png": [":-!", ":!"],
    "/static/images/smiles/tango/sun.png": ["(#)"],
    "/static/images/smiles/tango/rainbow.png": ["(R)", "(r)"],
    "/static/images/smiles/tango/shock.png": [":-O", ":o", ":O", ":-o"]
}
function markup(text){
    var out;
    var tags = {};
    function removeTags(name) {
        function wrapper(str, p1) {
            var key = ("" + Math.random()).replace('0.','')
            tags[key] = p1
            return '['+name+':'+key+']'
        }
        return wrapper
    }

    function insertTags(pattern){
        function wrapper(str, p1, p2) {
            return pattern.format(tags[p1]).trim()
        }
        return wrapper
    }

    out = text.replace('<', '&lt;').replace('>', '&gt;')
    out = out.replace('...', '&hellip;')

    out = out.replace(/(^|\s)+--(\s|$)+/gi, "$1&mdash;$2")

    out = out.replace(/\[raw](.*?)\[\/raw]/gi, removeTags('raw'))
    out = out.replace(/\[code](.*?)\[\/code]/gi, removeTags('code'))

    out = out.replace(/\/\/\/(.+?)\/\/\//gi, '<i>$1</i>')
    out = out.replace(/\+\+\+(.+?)\+\+\+/gi, '<b>$1</b>')
    out = out.replace(/---(.+?)---/gi, '<del>$1</del>')
    out = out.replace(/___(.+?)___/gi, '<ins>$1</ins>')

    out = out.replace(/\[raw:(.*?)]/gi, insertTags('{0}'))
    out = out.replace(/\[code:(.*?)]/gi, insertTags('<code>{0}</code>'))

    out = addSmiles(out)
    return out
}

function addSmiles(text){
    for(var img in smiles) {
        for(var i in smiles[img]){
            text = text.replace(smiles[img][i], '<img src="'+img+'" class="smile" alt=""/>')
        }
    }
    return text
}