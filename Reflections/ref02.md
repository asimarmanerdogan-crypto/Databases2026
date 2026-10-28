# Reflection 02 - Data contracts and legacy schemas

## Take-away

I learned that a database needs clear rules about how records are identified and connected. My main takeaway is that naming a column like a key is not enough. The database also needs the right constraints.

## What was good?

The Users and UserProfiles example gave me a concrete way to look at keys. The same user_id can be both a primary key and a foreign key.

## What was difficult?

The hardest part was understanding what the different keys are and how they work. I needed time to understand the difference between primary, foreign, natural and surrogate keys.

## Exploration and show stoppers

The shared PK/FK example was an interesting point from our discussion. I still need more practice choosing keys and explaining why a table needs them.

## Interaction with peers and instructors

I worked with Habiba and discussed database keys with other classmates in person. We compared the key types and talked about a column being both PK and FK. The [study log](../Module02/study-log.md#agreed-learning-pod-discussion) records the example and shared diagram.

## How did you verify AI suggestions?

I used AI explanations to help with the concepts. The [checks in my portfolio](../Module02/verification.txt), prepared and run with AI assistance, test duplicate keys, missing references and invalid values. For example, a job pointing to a missing machine should be rejected. These results give a concrete check of the suggested design.

## Help and extra work

Working with Habiba and the other classmates gave us a chance to compare our understanding and help each other. I also used AI to explain the parts I found difficult. I want to become more confident explaining the key choices myself.
