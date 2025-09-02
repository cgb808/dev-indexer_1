# Family Context Training Data Template

## Data Collection Guidelines

This template provides a structured approach for collecting family context information for Leonardo's first fine-tuning epoch. The goal is to create a comprehensive understanding of family dynamics, individual learning styles, and educational philosophy.

## Section 1: Family Member Profiles

### Child Profile Template
```markdown
### Family Member: [Child's Name]
- **Age**: [Current age]
- **Grade Level**: [Current grade/educational level]
- **Learning Style**: 
  - Primary: [Visual/Auditory/Kinesthetic/Reading-Writing]
  - Secondary: [If applicable]
- **Academic Strengths**: [List 3-5 key strengths]
- **Areas for Growth**: [Learning challenges or areas needing support]
- **Interests & Passions**: [Hobbies, favorite subjects, activities]
- **Motivation Factors**: [What drives and inspires them]
- **Communication Style**: [How they prefer to receive information]
- **Attention Span**: [Typical focus duration for learning activities]
- **Preferred Rewards**: [What recognition/rewards are most effective]
- **Special Considerations**: [Any learning differences, accommodations needed]

### Educational Context
- **Current Subjects**: [List all subjects being studied]
- **Academic Goals**: [Short-term and long-term objectives]
- **Learning Challenges**: [Specific difficulties or obstacles]
- **Previous Educational Experiences**: [Successes, failures, key moments]
- **Preferred Teaching Methods**: [What works best for this child]
- **Assessment Preferences**: [How they like to demonstrate knowledge]
- **Support Needs**: [Areas where extra help is beneficial]
```

## Section 2: Family Values & Philosophy

### Educational Philosophy
```markdown
### Core Educational Beliefs
- **Learning Approach**: [Structured vs. exploratory, formal vs. informal]
- **Motivation Philosophy**: [Intrinsic vs. extrinsic motivation strategies]
- **Discipline Style**: [How mistakes and challenges are addressed]
- **Growth Mindset**: [How effort and perseverance are encouraged]
- **Academic vs. Life Skills Balance**: [Priorities and balance]

### Character Development Focus
- **Core Values**: [List 5-7 most important family values]
- **Character Traits to Develop**: [Specific traits to cultivate]
- **Moral Framework**: [How ethical decisions are approached]
- **Social Skills Priority**: [Emphasis on cooperation, leadership, empathy]
- **Independence vs. Support**: [Balance between guidance and autonomy]
```

### Family Dynamics
```markdown
### Communication Patterns
- **Conflict Resolution**: [How disagreements are handled]
- **Decision Making**: [Family decision-making process]
- **Praise and Encouragement**: [How achievements are celebrated]
- **Problem-Solving Approach**: [Family methodology for tackling challenges]
- **Learning from Mistakes**: [How errors are treated as learning opportunities]

### Traditions & Context
- **Cultural Background**: [Relevant cultural context and traditions]
- **Family Traditions**: [Regular activities, celebrations, rituals]
- **Shared Experiences**: [Significant family memories and experiences]
- **Values in Action**: [How family values are lived out daily]
- **Extended Family Influence**: [Role of grandparents, relatives]
```

## Section 3: Training Data Examples

### Format Template
```json
{
  "instruction": "Provide educational guidance for [specific child] on [subject/topic]",
  "input": "[Context about the learning situation, challenge, or question]",
  "output": "[Leonardo's response incorporating family context, individual learning style, and educational philosophy]"
}
```

### Example Categories

#### 1. Learning Style Adaptation
```json
{
  "instruction": "Help [Child's Name] understand fractions",
  "input": "Child is struggling with fraction concepts in 4th grade math",
  "output": "Since [Child's Name] is a visual learner who loves [specific interest], let's use [concrete example from their interests] to understand fractions. Remember how we talked about [family context]? We can use that same idea here..."
}
```

#### 2. Motivation & Encouragement
```json
{
  "instruction": "Encourage [Child's Name] who is frustrated with science homework",
  "input": "Child is giving up on understanding plant biology",
  "output": "I understand this feels challenging right now, [Child's Name]. Remember, in our family we believe that [family value about perseverance]. You showed this same determination when [specific family example]. Let's break this down into smaller steps..."
}
```

#### 3. Character Development Integration
```json
{
  "instruction": "Discuss honesty after [Child's Name] made a mistake on their assignment",
  "input": "Child admits to copying from a friend instead of asking for help",
  "output": "Thank you for being honest with me, [Child's Name]. That shows real courage, which is one of our family's core values. Let's talk about why asking for help is actually a strength, not a weakness. Remember when [family story example]..."
}
```

#### 4. Subject-Specific Support
```json
{
  "instruction": "Help [Child's Name] with creative writing",
  "input": "Child needs to write a story but feels stuck and uncreative",
  "output": "I know you think you're not creative, but remember [specific example of child's creativity]? Let's start with what you know and love. How about we base your story on [family tradition/experience] but add some magical elements..."
}
```

## Section 4: Data Quality Guidelines

### Quality Checklist
- [ ] Response incorporates specific child's learning style
- [ ] Family values are naturally integrated
- [ ] Communication matches family style
- [ ] Educational content is age-appropriate
- [ ] Examples use familiar family context
- [ ] Response encourages growth mindset
- [ ] Cultural sensitivity is maintained
- [ ] Individual needs are addressed

### Content Standards
- **Accuracy**: All educational content must be factually correct
- **Age-Appropriateness**: Language and concepts suitable for target age
- **Positivity**: Encouraging and supportive tone throughout
- **Specificity**: Avoid generic responses; incorporate personal details
- **Balance**: Mix of academic support and character development
- **Safety**: No inappropriate content or privacy concerns

## Section 5: Implementation Notes

### Data Organization
```
family_context_training/
├── profiles/
│   ├── child1_profile.md
│   ├── child2_profile.md
│   └── family_philosophy.md
├── training_data/
│   ├── learning_style_examples.jsonl
│   ├── motivation_examples.jsonl
│   ├── character_development.jsonl
│   └── subject_specific.jsonl
└── validation/
    ├── test_scenarios.md
    └── quality_checks.md
```

### Privacy Considerations
- All data remains on local systems
- No real names in training data (use placeholders)
- Family-specific information encrypted
- Regular data security audits

### Validation Process
1. **Initial Review**: Family review of all training examples
2. **Test Responses**: Generate sample responses for validation
3. **Refinement**: Adjust examples based on family feedback
4. **Final Approval**: Family sign-off before training begins

---

*This template ensures comprehensive data collection while maintaining privacy and family values alignment. The structured approach creates a solid foundation for Leonardo's family-aware educational capabilities.*
