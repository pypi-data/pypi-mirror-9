Touch and Multi-Touch Actions
=============================


# Touch actions

In order to accomodate mobile touch actions, and touch actions involving
multiple pointers, the Selenium 3.0 draft specifies ["touch gestures"](https://dvcs.w3.org/hg/webdriver/raw-file/tip/webdriver-spec.html#touch-gestures) and ["multi actions"](https://dvcs.w3.org/hg/webdriver/raw-file/tip/webdriver-spec.html#multiactions-1), which build upon the touch actions.

The API is built around `TouchAction` objects, which are chains of one or more actions to be performed in a sequence. The actions are:


## `perform`

The `perform` method sends the chain to the server in order to be enacted. It also empties the action chain, so the object can be reused. It will be at the end of all single action chains, but is unused when writing multi-action chains.


## `tap`

The `tap` method stands alone, being unable to be chained with other methods. If you need a `tap`-like action that starts a longer chain, use `press`.

It can take either an element with an optional x-y offset, or absolute x-y coordinates for the tap, and an optional count.

```python
el = self.driver.find_element_by_accessibility_id('Animation')
action = TouchAction(self.driver)
action.tap(el).perform()
el = self.driver.find_element_by_accessibility_id('Bouncing Balls')
self.assertIsNotNone(el)
```


## `press`

The `press` action can start an sequence of actions, being a touch at a particular
element or position. If both an element and a position are given, the position is
taken as an offset from the top left corner of the element.

To press and immediately release, chain with a `release`:

```python
el = driver.find_element_by_name('Animation')
action = TouchAction(self.driver)
action.press(el).release().perform()
# or, action.press(el, 100, 10).release().perform()

el = driver.find_element_by_name('Bouncing Balls')
assertIsNotNone(el)
```


## `long_press`

The `long_press` action is the same as `press`, but with a pause (by default, one
second). Passing in a `duration`, in milliseconds, allows you to set how long to
pause.

Assuming you have a context menu associated with the element named `People Names`,


```python
el = self.driver.find_element_by_name('People Names')
action.long_press(el).perform()

# 'Sample menu' only comes up with a long press, not a tap
el = self.driver.find_element_by_name('Sample menu')
self.assertIsNotNone(el)
```


## `move_to`

After a `press` action, a `move_to` can be added to the chain. This will move the
pointer to another element or point, allowing


## `wait`


## `cancel`


## `release`


# Multi-touch actions

In addition to chains of actions performed with in a single gesture, it is also possible to perform multiple chains at the same time, to simulate multi-finger actions. This is done through building a `MultiAction` object that comprises a number of individual `TouchAction` objects, one for each "finger".

Given two lists next to each other, we can scroll them independently but simultaneously:

```python
els = self.driver.find_elements_by_class_name('listView')
a1 = TouchAction()
a1.press(els[0]) \
    .move_to(x=10, y=0).move_to(x=10, y=-75).move_to(x=10, y=-600).release()

a2 = TouchAction()
a2.press(els[1]) \
    .move_to(x=10, y=10).move_to(x=10, y=-300).move_to(x=10, y=-600).release()

ma = MultiAction(self.driver, els[0])
ma.add(a1, a2)
ma.perform();
```
