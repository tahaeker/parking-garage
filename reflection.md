# Personal Reflection

**Taha Yasin Eker — 230201042**

At first, I planned to pass the truck's entry time as a constructor argument. I then saw that I could use `LocalDateTime.now()` to get the system time and pass it to the superclass constructor. The test still failing after this change confused me. I had never written a test file before, and this was my first time reading test output in detail. I initially struggled to understand `ERROR`, `FAILURE`, and the exception messages.

I learned that `assertThrows` expects an exception. After I recorded the entry time, the fee could be calculated, but the test still expected an error. I thought the test might have been written to demonstrate the old problem, although I cannot be certain of its intended purpose. I kept the code that correctly records the entry time.

In the motorcycle example, I saw that null was passed to the method. Calling `getWidth()` without a parking-space object caused the failure. I added an `if (spot == null)` check to return false.

Next time, I will first check what the assertion expects and which project line appears in the stack trace. In an unfamiliar inheritance hierarchy, I will also check which superclass constructor initializes the fields and which overridden method actually runs.
