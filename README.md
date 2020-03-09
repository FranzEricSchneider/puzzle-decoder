# puzzle-decoder
Have a puzzle sheet in a cipher

Notes:
I got a solution to the puzzle, so I'm going to leave this repo for now. There's a number of messy things, TODOs, and unfinished tests, but I don't feel a need to keep working on it once the solution is obtained. Maybe if I need something similar in the future I'll start from here.

Thoughts about working on a simple substitution cipher.
* Transcription errors suck. In a couple of places I mis-translated things from cipher to numbers. There were two characters that looked like slightly different T shapes and I mis-transcribed them in a few places. This made convergence harder. Maybe make a better tool to check correctness.
* The strategy that ended up working best was only half-automated. I would generate a series of keys, look for portions of notable words, and then try poking the key closer to the answer by hand. If I wanted to automate this completely, I'd have to figure out how to score words by closeness to a solution (which is what I was doing by eye) and try specific interventions. Hard to get right. A simpler intermediate step would be to make a quick command line interface that would allow viewing of the current key and easy substitution. As it was I was copying values around into files and re-running the file.
* The score was based purely on number of English words. Scoring longer words higher would likely be good, because explaining a longer word is harder. Maybe score by portion of text explained?
* Likewise, oftentimes there'd be unusual words (unlikely to be the solution) that scored just as highly as common words because they were both ruled to be real. How about altering the scoring by some commonality metric?
* If a commonality metric is included, there should be a mechanism to choose some expected words by hand that aren't necessarily common in English but you may expect to show up.
* For speed reasons we should, once we're past the midpoint, clear out all of the really low scoring keys and just focus on polishing the top performers
* A really useful thing a human can do right now is knock out solutions that are English but have gotten locked in. For example, "ok" or "ox" gets locked in instead of "of", "pith" gets locked in instead of "with", and "par" gets locked in instead of "war". To further automate things, something that occasionally knocks out letters would be useful
