# Building Wordle with Flask and Datastar - Video Transcript

## Introduction

Hello there. We are going to rebuild the Wordle game with Flask. I understand you want to use Datastar to see all the cool stuff that other people are making with it, but you really like your synchronous framework - just the request-response model. And you're a bit scared. And I am a bit scared too of having to listen to connections because that means that at one point you're going to have to use async obviously, but you're also going to have some while loops running in your server. And if you're not very experienced like I am, you might find it a bit frightening.

This is why I wanted to create this demo where we are going to rebuild the Wordle game with a simple request-response model and just show you how smooth everything is. Because there are a lot of stuff you can still do with Datastar even if you use a synchronous framework.

## Demo Overview

Let's start with the demo first. So, we have levels of difficulty: easy, medium, hard, very very hard, and a secret difficulty level (but I'm not showing this in this video - you're going to have to check the website). Let's start in easy mode. And you can see how smooth the transition was.

We are not going to use anything but Flask and Datastar to achieve this result, I promise.

_[Demo gameplay showing French words like "piano", "lampe", "velos", "saloon"]_

We see that we succeeded the game. A little panel appeared and I can click "play again" and you see that the address bar is still the same and I can keep going like this. I refresh. I am back at the start menu. I click easy. I have a new game. Very functional, very simple. And we are going to see this with just Flask.

## Technology Stack and Dependencies

We are going to use, of course, Flask - just the basic stuff: render_template, session, redirect, url_for. We are going to try to stick to the request-response model. Some (flask) limiter that I use because it is live on my website, a choice to choose from words, and we are going to use the SDK of Datastar with the server-sent event generator.

As server-sent events can send zero to n events, we're just going to use this with n equals 1 - request response. But you are going to see that as it is an SSE response on a Datastar frontend, you get a lot of cool stuff for free.

We are still going to use TinyDB to store the tries. We are still going to use a list of words. And if you want more details about this, please check the other video where I do it with Quart in async mode and CQRS pattern. It's also really interesting.

## Core Implementation

### Configuration and Setup

Let's start with some configuration: the limiter, the database, the get_color function. I'm not going to spend a lot of time on this. It's just given the word to guess and the attempt that was made by the user, return the correct coloring that we want.

### The View Function

The view function will create the HTML that we want for the game. So we take from the data that we stored:

- The number of tries
- The number of letters in the word to guess
- The attempts that were made by the user
- The status of the game

If the game is won, we add an overlay to congratulate the player. If the game is lost, we add an overlay where we are going to tell them what the word was. Otherwise, we don't add any overlay.

We start with the main element. We still use fat morphs, put an ID on main, and send the main element. Datastar will do the rest.

### Custom Events with data-on

The first thing that we are going to see here is the `data-on-wordle`. What is `data-on-wordle`? You can use `data-on` with a custom event. And what we did here, if you saw the video about the Quart version of the Wordle game, we tried to carve the signals into something that we want before triggering the post event.

What we did here is we just define a custom web component called "WordleLine". And this web component is going to have a lot of logic inside it - not to add too many letters, to remove them, verify some stuff. So all the logic will be encapsulated in this web component.

### Web Component Logic

You see that this web component listens to keydown events, changes its length, uses all sorts of logic inside it. You can check the code as usual in the description. It does a regex match on the key that was pressed. And if I press enter and I have the correct value - so I have the correct number of letters to send to the server - everything is fine and the web component is happy. It will dispatch a custom event name that we are going to catch in Datastar.

So props down, events up. The web component wherever it is on the page will send an event. The main element will catch it with `data-on-wordle` and post to `/attempt` with the value of the event, which is obviously going to be just the letters sent by the user.

### Network Requests

As you can see here, if I go into my network tab, when I press enter, we have a POST request to `/attempt/logic`. Very simple stuff. And then, as you are used to, I just catch with a Flask route the letters that were sent. I perform my checks. I perform my database operations. So I check if the word is correct. I check for the colors that I want to render afterwards. I check if the game is over. Stuff like that.

I update the database and then I call the view function (the same one) with the new data. So the view function will create the new HTML that I want and then I can use merge fragments to replace it seamlessly into the page. And that is very smooth as you can see (smirk).

### Game Grid Structure

We continue on our view function. After we have done this `data-on-wordle`, we have also an indicator here. We add the overlay if needed if the game is over. This is the indicator with fetching signal.

And then I'm going to put a grid with obviously the number of tries - so the number of lines that you give to the user. Then for every attempt that they already made, we take the colors and we put them. We have green, yellow, chocolate (which was better), black, and we add squares and squares and squares inside a line.

After the attempts, if the game is not over, we add a wordle-line. So, this is the web component that we define in the JavaScript. We pass it a property of length - so the number of letters in this wordle line. Web components are really useful for this. And then we complete with the number of attempts left with just empty squares.

## Flask Routes and Game Logic

### Difficulty Selection

I'm going to show you the rest of the Flask stuff that you are going to have to do. For example, give a database to a user. I explain a lot of this in more detail in the Quart version, but you see that this is really simple Quart stuff.

`index` will return index for the difficulty matching something very simple. You see that every difficulty on the index.html page posts to `/difficulty/easy`, `/difficulty/medium`, whatever, and we catch that as an argument with the Flask router.

Then we put it in the database for the user. If you put easy, then that means we take a five-letter word, we give it seven tries, five letters for each try. We put that all in the database, we call the view function on this fresh data, and like before, just use merge fragments with `fragments=html` to do the fat morph on main. And that's how you get this really seamless transition between the two.

### Database Considerations

One little trick that is important to mention here: TinyDB is not fit for contexts when you have multiple workers, multiple threads because it is incrementing an internal counter for performance of the ID of documents. One trick that you can do here is just use the time as the doc ID to suppress the risk of conflicts of different workers accessing the database. Stupid trick, really effective. And you get to use TinyDB in a multi-threaded environment, which is kind of nice.

### Starting a New Game

Finally, how do we start a new game? You can see in the overlay here that I just use a simple link `href` to a `/new-game` route. And the new game route will just clear the session - so clear the database, refresh the page with a redirect to index. And because the user will then be accessing the index function, I will before the request give it another database entry, return index.html. Simple as that.

## CSS Tricks and Animations

The last part is going to be the CSS tricks that I used. Two main tricks:

### Overlay Timing

First, in the overlay, because we want the overlay to appear let's say two seconds after the user put the right answer or has tried all their attempts. It was very easy in an async context to just make the server wait and because you have an open connection, send the overlay. You can't do that in a request-response model.

**shows demo how we need time to animate**

You want to have this little delay so that the last attempt can have time to animate. Just really simple. The overlay - you give it a pop animation from opacity equals zero to one after 1 second over 1 second. So it's baked in the HTML and you use CSS to time it properly.

### Square Color Animation Delays

And talking about timing properly, the second CSS trick is of course the little delay when the squares change colors. So for that we are going to use a CSS attribute `data-delay`. So this is not in Datastar but you can still do this with CSS.

Give `data-*` to something. We give it a delay incrementing based on the number of tries. And then in CSS we can capture that value with `attr()`. Say we want this to be interpreted as a time with a fallback of 0 seconds.

So because I have a lot of fine-grain control over the HTML that I send, I can send attributes that I want to be caught by CSS this way. So we get this nice motion. I really should have done six letters. This nice delay effect (color squares from left-to-right) with pure CSS.

## Conclusion

That's it for today. As you can see, it was very, very easy to just keep the request-response structure, to just keep Flask. And if that's what you know best, you can still use Datastar for its frontend reactivity and for the convenience of using merge fragments and have this really nice merges giving the feel of an SPA to a synchronous request-response app.

This is live on my personal website for the moment. So, you can go to [leg.ovh](leg.ovh) (link in the description as always). You can try your best. Let me know in the comments if one of you manages to crack the "Hackerman" difficulty. I would be really interested if someone can solve that. And also go check it because there is a secret difficulty. But maybe you're better off joining the Discord of Datastar to know what it is.

Not saying anything more than that except that you can click on the title and I have a nice animation. And I hope that you enjoy the video. As always, code is in the comments. I really hope that you will feel reassured by the fact that you can use Datastar with Flask just fine.

And see you later.
