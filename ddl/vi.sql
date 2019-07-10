--
-- VI database ddl and initial data
--



CREATE SCHEMA vi;


ALTER SCHEMA vi OWNER TO vi;

--
-- Name: answer; Type: TABLE; Schema: vi; Owner: vi
--

CREATE TABLE vi.answer (
    id serial PRIMARY KEY,
    question text NOT NULL,
    time_received timestamp without time zone NOT NULL,
    answer text NOT NULL,
    "user" integer NOT NULL
);


ALTER TABLE vi.answer OWNER TO vi;


--
-- Name: answer_result; Type: TABLE; Schema: vi; Owner: vi
--

CREATE TABLE vi.answer_result (
    answer integer NOT NULL,
    result integer NOT NULL
);


ALTER TABLE vi.answer_result OWNER TO vi;


--
-- Name: answer_result answer_result_pkey; Type: CONSTRAINT; Schema: vi; Owner: vi
--

ALTER TABLE ONLY vi.answer_result
    ADD CONSTRAINT answer_result_pkey PRIMARY KEY (answer, result);

--
-- Name: index; Type: TABLE; Schema: vi; Owner: vi
--

CREATE TABLE vi.index (
    name text PRIMARY KEY,
    maxpoints integer NOT NULL
);


ALTER TABLE vi.index OWNER TO vi;

--
-- Name: indexcomponent; Type: TABLE; Schema: vi; Owner: vi
--

CREATE TABLE vi.indexcomponent (
    name text PRIMARY KEY,
    maxpoints integer NOT NULL,
    index text NOT NULL,
    info text NOT NULL,
    recommendation text NOT NULL
);


ALTER TABLE vi.indexcomponent OWNER TO vi;

--
-- Name: indexsubcomponent; Type: TABLE; Schema: vi; Owner: vi
--

CREATE TABLE vi.indexsubcomponent (
    name text PRIMARY KEY,
    maxpoints integer NOT NULL,
    index_component text NOT NULL,
    info text NOT NULL,
    recommendation text NOT NULL
);


ALTER TABLE vi.indexsubcomponent OWNER TO vi;

--
-- Name: indexsubcomponent_question; Type: TABLE; Schema: vi; Owner: vi
--

CREATE TABLE vi.indexsubcomponent_question (
    indexsubcomponent text NOT NULL,
    question text NOT NULL
);


ALTER TABLE vi.indexsubcomponent_question OWNER TO vi;

--
-- Name: indexsubcomponent_question indexsubcomponent_question_pkey; Type: CONSTRAINT; Schema: vi; Owner: vi
--

ALTER TABLE ONLY vi.indexsubcomponent_question
    ADD CONSTRAINT indexsubcomponent_question_pkey PRIMARY KEY (indexsubcomponent, question);


--
-- Name: question; Type: TABLE; Schema: vi; Owner: vi
--

CREATE TABLE vi.question (
    name text PRIMARY KEY,
    info text NOT NULL,
    qtext text NOT NULL
);


ALTER TABLE vi.question OWNER TO vi;

--
-- Name: result; Type: TABLE; Schema: vi; Owner: vi
--

CREATE TABLE vi.result (
    id serial PRIMARY KEY,
    time_generated timestamp without time zone NOT NULL,
    points integer NOT NULL,
    maxforanswered integer NOT NULL,
    index text NOT NULL,
    "user" integer NOT NULL
);


ALTER TABLE vi.result OWNER TO vi;

--
-- Name: resultcomponent; Type: TABLE; Schema: vi; Owner: vi
--

CREATE TABLE vi.resultcomponent (
    id serial PRIMARY KEY,
    result integer NOT NULL,
    points integer NOT NULL,
    maxforanswered integer NOT NULL,
    index_component text NOT NULL
);


ALTER TABLE vi.resultcomponent OWNER TO vi;


--
-- Name: resultsubcomponent; Type: TABLE; Schema: vi; Owner: vi
--

CREATE TABLE vi.resultsubcomponent (
    id serial PRIMARY KEY,
    result_component integer NOT NULL,
    points integer NOT NULL,
    maxforanswered integer NOT NULL,
    index_sub_component text NOT NULL
);


ALTER TABLE vi.resultsubcomponent OWNER TO vi;


--
-- Name: token; Type: TABLE; Schema: vi; Owner: vi
--

CREATE TABLE vi.token (
    id serial PRIMARY KEY,
    jti text NOT NULL,
    token_type text NOT NULL,
    "user" integer NOT NULL,
    revoked boolean NOT NULL,
    expires timestamp without time zone NOT NULL
);


ALTER TABLE vi.token OWNER TO vi;


--
-- Name: user; Type: TABLE; Schema: vi; Owner: vi
--

CREATE TABLE vi."user" (
    id serial PRIMARY KEY,
    email text NOT NULL,
    pword text NOT NULL,
    first_name text NOT NULL,
    birth_date date NOT NULL,
    gender text NOT NULL,
    postal_code text NOT NULL,
    role text NOT NULL,
    last_login timestamp without time zone,
    last_notification timestamp without time zone
);


ALTER TABLE vi."user" OWNER TO vi;



--
-- Data for Name: index; Type: TABLE DATA; Schema: vi; Owner: vi
--

COPY vi.index (name, maxpoints) FROM stdin;
Vitality Index	1000
\.


--
-- Data for Name: indexcomponent; Type: TABLE DATA; Schema: vi; Owner: vi
--

COPY vi.indexcomponent (name, maxpoints, index, info, recommendation) FROM stdin;
EXERCISE	300	Vitality Index	not yet	not yet
MEDICAL	220	Vitality Index	not yet	not yet
NUTRITION	100	Vitality Index	not yet	not yet
PERCEPTION	80	Vitality Index	not yet	not yet
SOCIAL	300	Vitality Index	not yet	not yet
\.


--
-- Data for Name: indexsubcomponent; Type: TABLE DATA; Schema: vi; Owner: vi
--

COPY vi.indexsubcomponent (name, maxpoints, index_component, info, recommendation) FROM stdin;
SYS	10	MEDICAL	information for MEDICAL.SYS	recommendation for MEDICAL.SYS
DIA	10	MEDICAL	information for MEDICAL.DIA	recommendation for MEDICAL.DIA
LDL	10	MEDICAL	information for MEDICAL.LDL	recommendation for MEDICAL.LDL
HDL	10	MEDICAL	information for MEDICAL.HDL	recommendation for MEDICAL.HDL
TRI	20	MEDICAL	information for MEDICAL.TRI	recommendation for MEDICAL.TRI
RHR	10	MEDICAL	information for MEDICAL.RHR	recommendation for MEDICAL.RHR
TOBACCO7	0	MEDICAL	information for MEDICAL.TOBACCO7	recommendation for MEDICAL.TOBACCO7
TOBACCO180	0	MEDICAL	information for MEDICAL.TOBACCO180	recommendation for MEDICAL.TOBACCO180
NUMFRUITSSERVS	20	NUTRITION	information for NUTRITION.NUMFRUITSSERVS	recommendation for NUTRITION.NUMFRUITSSERVS
NUMVEGSERVS	30	NUTRITION	information for NUTRITION.NUMVEGSERVS	recommendation for NUTRITION.NUMVEGSERVS
NUMFRUITANDVEG	30	NUTRITION	information for NUTRITION.NUMFRUITANDVEG	recommendation for NUTRITION.NUMFRUITANDVEG
NUMDRINKS	10	NUTRITION	information for NUTRITION.NUMDRINKS	recommendation for NUTRITION.NUMDRINKS
NUMCAFDRINKS	0	NUTRITION	information for NUTRITION.NUMCAFDRINKS	recommendation for NUTRITION.NUMCAFDRINKS
NUMWATERDRINKS	10	NUTRITION	information for NUTRITION.NUMWATERDRINKS	recommendation for NUTRITION.NUMWATERDRINKS
NUMALCDRINKS	0	NUTRITION	information for NUTRITION.NUMALCDRINKS	recommendation for NUTRITION.NUMALCDRINKS
PAINLIFE	20	PERCEPTION	information for PERCEPTION.PAINLIFE	recommendation for PERCEPTION.PAINLIFE
HEALTHLIFE	20	PERCEPTION	information for PERCEPTION.HEALTHLIFE	recommendation for PERCEPTION.HEALTHLIFE
RELIEDOTHERS	20	PERCEPTION	information for PERCEPTION.RELIEDOTHERS	recommendation for PERCEPTION.RELIEDOTHERS
PERCEIVEDHEALTH	20	PERCEPTION	information for PERCEPTION.PERCEIVEDHEALTH	recommendation for PERCEPTION.PERCEIVEDHEALTH
WORKCOMP	5	SOCIAL	information for PSYCHOSOCIAL.WORKCOMP	recommendation for PSYCHOSOCIAL.WORKCOMP
WORKGRAT	15	SOCIAL	information for PSYCHOSOCIAL.WORKGRAT	recommendation for PSYCHOSOCIAL.WORKGRAT
WORKCAR	10	SOCIAL	information for PSYCHOSOCIAL.WORKCAR	recommendation for PSYCHOSOCIAL.WORKCAR
WORKHOURS	20	SOCIAL	information for PSYCHOSOCIAL.WORKHOURS	recommendation for PSYCHOSOCIAL.WORKHOURS
WORKSTRESS	15	SOCIAL	information for PSYCHOSOCIAL.WORKSTRESS	recommendation for PSYCHOSOCIAL.WORKSTRESS
GROUPEVENTS	10	SOCIAL	information for PSYCHOSOCIAL.GROUPEVENTS	recommendation for PSYCHOSOCIAL.GROUPEVENTS
NONWORKACTIVITIES	15	SOCIAL	information for PSYCHOSOCIAL.NONWORKACTIVITIES	recommendation for PSYCHOSOCIAL.NONWORKACTIVITIES
NONWORKGRAT	20	SOCIAL	information for PSYCHOSOCIAL.NONWORKGRAT	recommendation for PSYCHOSOCIAL.NONWORKGRAT
EXERCISE	150	EXERCISE	information for EXERCISE.EXERCISE	recommendation for EXERCISE.EXERCISE
DAYSEX	30	EXERCISE	information for EXERCISE.DAYSEX	recommendation for EXERCISE.DAYSEX
DAYSRES	15	EXERCISE	information for EXERCISE.DAYSRES	recommendation for EXERCISE.DAYSRES
SETSRES	15	EXERCISE	information for EXERCISE.SETSRES	recommendation for EXERCISE.SETSRES
DAYSFLEX	15	EXERCISE	information for EXERCISE.DAYSFLEX	recommendation for EXERCISE.DAYSFLEX
MINSFLEX	15	EXERCISE	information for EXERCISE.MINSFLEX	recommendation for EXERCISE.MINSFLEX
DAYSBAL	15	EXERCISE	information for EXERCISE.DAYSBAL	recommendation for EXERCISE.DAYSBAL
MINSBAL	15	EXERCISE	information for EXERCISE.MINSBAL	recommendation for EXERCISE.MINSBAL
HOURSNONSED	30	EXERCISE	information for EXERCISE.HOURSNONSED	recommendation for EXERCISE.HOURSNONSED
BMI	40	MEDICAL	information for MEDICAL.BMI	recommendation for MEDICAL.BMI
MEDCONDS	110	MEDICAL	information for MEDICAL.MEDCONDS	recommendation for MEDICAL.MEDCONDS
NUMMEDS	0	MEDICAL	information for MEDICAL.NUMMEDS	recommendation for MEDICAL.NUMMEDS
NONWORKSTRESS	25	SOCIAL	information for PSYCHOSOCIAL.NONWORKSTRESS	recommendation for PSYCHOSOCIAL.NONWORKSTRESS
FINSTRESS	10	SOCIAL	information for PSYCHOSOCIAL.FINSTRESS	recommendation for PSYCHOSOCIAL.FINSTRESS
PRINETWORK	10	SOCIAL	information for PSYCHOSOCIAL.PRINETWORK	recommendation for PSYCHOSOCIAL.PRINETWORK
TOTALNETWORK	10	SOCIAL	information for PSYCHOSOCIAL.TOTALNETWORK	recommendation for PSYCHOSOCIAL.TOTALNETWORK
COMMUNITYCOH	5	SOCIAL	information for PSYCHOSOCIAL.COMMUNITYCOH	recommendation for PSYCHOSOCIAL.COMMUNITYCOH
COMMUNITYINTER	5	SOCIAL	information for PSYCHOSOCIAL.COMMUNITYINTER	recommendation for PSYCHOSOCIAL.COMMUNITYINTER
SOCIALSAT	20	SOCIAL	information for PSYCHOSOCIAL.SOCIALSAT	recommendation for PSYCHOSOCIAL.SOCIALSAT
EMOTIONALENRICH	30	SOCIAL	information for PSYCHOSOCIAL.EMOTIONALENRICH	recommendation for PSYCHOSOCIAL.EMOTIONALENRICH
SLEEPHOURS	10	SOCIAL	information for PSYCHOSOCIAL.SLEEPHOURS	recommendation for PSYCHOSOCIAL.SLEEPHOURS
SLEEPSAT	10	SOCIAL	information for PSYCHOSOCIAL.SLEEPSAT	recommendation for PSYCHOSOCIAL.SLEEPSAT
LIFESAT	10	SOCIAL	information for PSYCHOSOCIAL.LIFESAT	recommendation for PSYCHOSOCIAL.LIFESAT
ENERGYLVL	10	SOCIAL	information for PSYCHOSOCIAL.ENERGYLVL	recommendation for PSYCHOSOCIAL.ENERGYLVL
LIFECONTROL	10	SOCIAL	information for PSYCHOSOCIAL.LIFECONTROL	recommendation for PSYCHOSOCIAL.LIFECONTROL
OPTIMISM	10	SOCIAL	information for PSYCHOSOCIAL.OPTIMISM	recommendation for PSYCHOSOCIAL.OPTIMISM
DIRECTION	10	SOCIAL	information for PSYCHOSOCIAL.DIRECTION	recommendation for PSYCHOSOCIAL.DIRECTION
ANXIETYLVL	10	SOCIAL	information for PSYCHOSOCIAL.ANXIETYLVL	recommendation for PSYCHOSOCIAL.ANXIETYLVL
NEEDSMET	10	SOCIAL	information for PSYCHOSOCIAL.NEEDSMET	recommendation for PSYCHOSOCIAL.NEEDSMET
RELATIONSHIPS	10	SOCIAL	information for PSYCHOSOCIAL.RELATIONSHIPS	recommendation for PSYCHOSOCIAL.RELATIONSHIPS
OVERALLHAPPY	10	SOCIAL	information for PSYCHOSOCIAL.OVERALLHAPPY	recommendation for PSYCHOSOCIAL.OVERALLHAPPY
OVERALLSTRESS	10	SOCIAL	information for PSYCHOSOCIAL.OVERALLSTRESS	recommendation for PSYCHOSOCIAL.OVERALLSTRESS
OVERALLANXIETY	10	SOCIAL	information for PSYCHOSOCIAL.OVERALLANXIETY	recommendation for PSYCHOSOCIAL.OVERALLANXIETY
OVERALLSAT	10	SOCIAL	information for PSYCHOSOCIAL.OVERALLSAT	recommendation for PSYCHOSOCIAL.OVERALLSAT
\.


--
-- Data for Name: indexsubcomponent_question; Type: TABLE DATA; Schema: vi; Owner: vi
--

COPY vi.indexsubcomponent_question (indexsubcomponent, question) FROM stdin;
BMI	Height
BMI	Weight
RHR	RestingHeartRate
DIA	DiastolicBloodPressure
SYS	SystolicBloodPressure
HDL	HDLCholesterol
LDL	LDLCholesterol
TRI	Triglycerides
MEDCONDS	NumberOfConditions
MEDCONDS	ConditionsManagedByDoctor
MEDCONDS	ConditionsManagedByLifestyle
NUMMEDS	NumberMedications
TOBACCO180	UsedTobaccoInPast6Months
TOBACCO7	UsedTobaccoInPast7Days
NUMDRINKS	NumberDrinks
NUMALCDRINKS	NumberAlcoholicDrinks
NUMCAFDRINKS	NumberCaffeinatedDrinks
NUMWATERDRINKS	NumberWaterDrinks
NUMFRUITANDVEG	NumberFruitServings
NUMFRUITANDVEG	NumberVegetableServings
NUMFRUITSSERVS	NumberFruitServings
NUMVEGSERVS	NumberVegetableServings
EXERCISE	MinutesPhysicalActivity
EXERCISE	MinutesVigorousExercise
EXERCISE	MinutesModerateExercise
DAYSBAL	DaysBalanceAgilityExercise
MINSBAL	MinutesBalanceAgilityActivity
DAYSEX	DaysPhysicalActivity
DAYSFLEX	DaysFlexibilityExercise
MINSFLEX	MinutesFlexibilityActivity
DAYSRES	DaysResistanceExercise
SETSRES	SetsResistanceExercise
HOURSNONSED	AverageHoursNonSedentary
PERCEIVEDHEALTH	OverallHealth
FINSTRESS	DifficultyPayingBills
COMMUNITYCOH	HaveNeighborThatCanBeReliedOn
COMMUNITYINTER	TimesMeetingSpeakingNonCloseFriends
PRINETWORK	TimesMeetingSpeakingFriends
TOTALNETWORK	TotalPrimarySecondaryFriends
SOCIALSAT	SocialSatisfaction
SOCIALSAT	FamilySatisfaction
SOCIALSAT	BalanceSatisfaction
EMOTIONALENRICH	SatisfactionTimeAlone
EMOTIONALENRICH	PetOwner
EMOTIONALENRICH	GratificationPetOwner
EMOTIONALENRICH	InRelationship
EMOTIONALENRICH	RelationshipSatisfaction
EMOTIONALENRICH	PhysicalSatisfaction
GROUPEVENTS	TimesLargeGroupActivities
NONWORKACTIVITIES	HoursLargeGroupActivities
NONWORKGRAT	GratificationLargeGroupActivities
NONWORKSTRESS	StressLargeGroupActivities
GROUPEVENTS	TimesSmallGroupActivities
NONWORKACTIVITIES	HoursSmallGroupActivities
NONWORKGRAT	GratificationSmallGroupActivities
NONWORKSTRESS	StressSmallGroupActivities
NONWORKACTIVITIES	HoursVolunteering
NONWORKGRAT	GratificationVolunteering
NONWORKSTRESS	StressVolunteering
NONWORKACTIVITIES	HoursHelpingFriendsFamily
NONWORKGRAT	GratificationHelpingFriendsFamily
NONWORKSTRESS	StressHelpingFriendsFamily
ANXIETYLVL	AnxietyLevel
DIRECTION	SenseOfDirection
ENERGYLVL	EnergyLevel
OPTIMISM	OptimisticAboutFuture
LIFECONTROL	HandleEverythingNeeded
LIFESAT	GoodAboutLife
NEEDSMET	NeedsBeingMet
OVERALLANXIETY	OverallAnxietyLevel
OVERALLHAPPY	OverallHappiness
OVERALLSAT	OverallLifeSatisfaction
OVERALLSTRESS	OverallStressLevel
RELATIONSHIPS	MeaningfulRelationships
SLEEPHOURS	SleepTime
SLEEPSAT	SatisfactionSleep
WORKHOURS	HoursWorked
WORKCAR	HoursInCarForWork
WORKCOMP	ComparisonHoursWorkedToDesired
WORKGRAT	GratificationFromWork
WORKSTRESS	StressFromWork
MEDCONDS	ConditionsAffectOnLife
PAINLIFE	PainInterferedWithActivities
RELIEDOTHERS	ReliedOnOthersForHelp
HEALTHLIFE	OtherFactorsInterferedWithActivities
\.


--
-- Data for Name: question; Type: TABLE DATA; Schema: vi; Owner: vi
--

COPY vi.question (name, info, qtext) FROM stdin;
Height	not yet	What is your height in inches?
Weight	not yet	What is your weight in pounds?
SystolicBloodPressure	not yet	What is your Systolic blood pressure?
ConditionsAffectOnLife	not yet	On a scale of 1 to 10, with 10 being the most problematic, to what degree are your day-to-day activities limited by any of your major health conditions?
UsedTobaccoInPast6Months	not yet	Have you used any tobacco products in the last 6 months?
UsedTobaccoInPast7Days	not yet	Have you used any tobacco products in the last 7 days?
NumberDrinks	not yet	Over the last 7 days, how many total drinks have you consumed on average per day  (including 8-oz. drinks of water, caffeinated beverages such as coffee or tea, soft drinks, juice, and electrolyte drinks or alcoholic beverage including 12-oz beer, 8-oz malt liquor, 5-oz of wine, 1.5-oz of distilled spirits)?
NumberVegetableServings	not yet	Over the last 7 days, how many portions of vegetables have you eaten on average per day? (one serving of vegetables includes one handful of cut raw, frozen, cooked, or canned vegetables)
MinutesPhysicalActivity	not yet	Altogether, over the past 7 days, approximately how many minutes total did you exercise (counting only sessions that included 10 consecutive minutes or longer)?
NumberFruitServings	not yet	Over the last 7 days, how many portions of fruit have you eaten on average per day? (one serving of fruit includes one handful of cut raw, frozen, cooked, or canned fruits)
MinutesVigorousExercise	not yet	Of those total minutes, how many were spent engaged in vigorous-intensity (as defined by an effort of 7 - 8 on a scale of 1 -10)? For example, running, playing tennis, biking, racquetball or similar activity, hiking uphill, or fast paced aerobic activities?
MinutesModerateExercise	not yet	Of those total minutes, how many were spent engaged in low to moderate-intensity (as defined by an effort of 5 - 6 on a scale of 1 - 10)? For example, walking at a moderate pace, dancing for leisure, weight training, housecleaning, playing golf, or gardening such as raking, hoeing, or mowing the lawn?
DaysBalanceAgilityExercise	not yet	Over the last 7 days, how many days did you participate in exercises that involve balance, agility, or coordination?
MinutesBalanceAgilityActivity	not yet	Altogether, over the past 7 days, approximately how many total minutes were spent engaged in balance, agility, or coordination activities?
DaysPhysicalActivity	not yet	Over the last 7 days, how many days did you engage in any kind of physical activity for 10 consecutive minutes or longer?
DaysFlexibilityExercise	not yet	Over the last 7 days, how many days did you participate in flexibility exercise (activities that seek to increase your range of motion)
MinutesFlexibilityActivity	not yet	Altogether, over the past 7 days, approximately how many total minutes were spent engaged in flexibility activities?
DaysResistanceExercise	not yet	Over the last 7 days, how many days did you participate in resistance exercise (activities that seek to increase muscle strength such as exercises that involve weight machines, free weights, or exercises in which you lift or hold your own body weight)
SetsResistanceExercise	not yet	Over the last 7 days, how many sets of resistance training did you do for each of your major muscle groups (chest, shoulders, upper and lower back, abdomen, hips, and legs)?
AverageHoursNonSedentary	not yet	Over the last 7 days, approximately how many hours per day on average did you spend in a non-sedentary position (i.e., were not sitting in a chair or laying down)?
DifficultyPayingBills	not yet	In thinking about the last month, how difficult is it for (you/your family) to meet monthly payments on (your/your family's bills)?
PetOwner	not yet	Do you currently have a cat, a dog, or another pet?
InRelationship	not yet	What is your relationship status?
TimesLargeGroupActivities	not yet	In thinking about the last month, how many times did you attend a meeting for a social cause or interest, attend a class/seminar, educational activity, or participate in an event/engagement?
HoursLargeGroupActivities	not yet	About how many hours did you spend per week (on average) engaged in these activities?
TimesSmallGroupActivities	not yet	In thinking about the last month, how many times did you share a meal, go shopping, take a walk or jog, or meet and share a beverage with a friend or family member not living with you?
HoursSmallGroupActivities	not yet	About how many hours did you spend per week (on average) engaged in these kinds of social activities?
HoursVolunteering	not yet	In thinking about the last month, how many hours per week (on average) did you spend volunteering for a non-religious organization, charity, school, religious organization, or hospital?
SleepTime	not yet	In thinking about the last 7 days, on a typical night how many hours did you sleep?
HoursWorked	not yet	In thinking about the last month, how many hours per week (on average) have you spent working in a paid job?
HoursInCarForWork	not yet	How many hours per week (on average) did you spend in your car because of your job?
GratificationFromWork	not yet	On a scale from 1 to 10, with 10 being the most, how much gratification did you receive from your work over the last month?
StressFromWork	not yet	On a scale from 1 to 10, with 10 being the highest how much stress did you experience because of your work over the last month?
RestingHeartRate	not yet	What is your resting heart rate in bpm?
HDLCholesterol	not yet	What is your HDL cholesterol?
LDLCholesterol	not yet	What is your LDL cholesteral?
Triglycerides	not yet	What are your Triglycerides?
ConditionsManagedByLifestyle	not yet	How many of your major medical conditions  are you successfully managing with medication or a health maintenance program?
NumberOfConditions	not yet	How many major medical conditions from the following list do you have?
NumberAlcoholicDrinks	not yet	Over the last 7 days, how many alcoholic drinks have you consumed on average per day?
NumberCaffeinatedDrinks	not yet	Over the last 7 days, how many caffeinated drinks have you consumed on average per day?
NumberWaterDrinks	not yet	Over the last 7 days, how many water drinks have you consumed on average per day?
OverallHealth	not yet	In thinking about your overall health today, would you say that your overall health is Excellent, Very Good, Good, Fair or Poor?
HaveNeighborThatCanBeReliedOn	not yet	Do you currently have at least one neighbor you feel you could go to if you needed something?
TimesMeetingSpeakingFriends	not yet	In thinking about the last month, how many people who you consider "friends" did you see or speak with by phone at least 4 times?
TotalPrimarySecondaryFriends	not yet	If you were in a pinch today and needed help, how many people (including friends, family, and acquaintances) in your community do you feel you could go to?
SocialSatisfaction	not yet	Overall during the last month, on a scale from 1 to 10, with 10 being the most, how satisfying has your social life been?
FamilySatisfaction	not yet	Overall during the last month, on a scale from 1 to 10, with 10 being the most, how satisfying has your family life been?
BalanceSatisfaction	not yet	Overall during the last month, on a scale from 1 to 10, with 10 being the most, how satisfied have you been with your balance between family, work, and social engagement?
SatisfactionTimeAlone	not yet	Thinking about the time spent awake and not working, during the last 7 days, on a scale from 1 to 10, with 10 being the most, how satisfied have you been with the time you have spent by yourself?
GratificationPetOwner	not yet	Thinking about the last 7 days, on a scale from 1 to 10, with 10 being the most, how much gratification would you say you got from the time you spent with your pet?
RelationshipSatisfaction	not yet	Overall during the last 7 days, on a scale from 1 to 10, with 10 being the most, how satisfied have you been with your relationship with your spouse/partner?
PhysicalSatisfaction	not yet	Overall during the last 7 days, on a scale from 1 to 10, with 10 being the most, how satisfied have you been with the intimacy between you and your partner?
GratificationLargeGroupActivities	not yet	On a scale from 1 to 10, with 10 being the most, how much gratification would you say you got from the time you spent engaged in these group activities over the last month?
StressLargeGroupActivities	not yet	On a scale from 1 to 10, with 10 being the highest how much stress did you experience from the time you spent in these group activities over the last month?
GratificationSmallGroupActivities	not yet	On a scale from 1 to 10, with 10 being the most, how much gratification would you say you got from the time you spent getting together with friends or family over the last month?
StressSmallGroupActivities	not yet	On a scale from 1 to 10, with 10 being the highest how much stress did you experience from the time you spent getting together with friends or family over the last month?
GratificationVolunteering	not yet	On a scale from 1 to 10, with 10 being the most, how much gratification would you say you got from the time you spent volunteering over the last month?
StressVolunteering	not yet	On a scale from 1 to 10, with 10 being the highest how much stress did you experience from the time you spent volunteering over the last month?
HoursHelpingFriendsFamily	not yet	In thinking about the last month, how many hours per week (on average) did you spend helping friends and family not living with you? (For example, providing care to a sick or disabled family member, running errands, making food for a sick friend, caring for a friend's child, caring for your grandchildren)
GratificationHelpingFriendsFamily	not yet	On a scale from 1 to 10, with 10 being the most, how much gratification would you say you got from the time you spent helping friends and family over the last month?
StressHelpingFriendsFamily	not yet	On a scale from 1 to 10, with 10 being the highest how much stress did you experience from the time you spent helping friends and family over the last month?
AnxietyLevel	not yet	In thinking about the last 7 days, on a scale of 1 to 10 with 10 being all the time and 1 being almost never, how much of the time have you felt like you were worrying a lot?
SenseOfDirection	not yet	In thinking about the last 7 days, on a scale of 1 to 10 with 10 being all the time and 1 being almost never, how much of the time have you felt connected to a sense of direction or purpose in your life?
EnergyLevel	not yet	In thinking about the last 7 days, on a scale of 1 to 10 with 10 being all the time and 1 being almost never, how much of the time have you felt like you had a lot of energy?
HandleEverythingNeeded	not yet	In thinking about the last 7 days, on a scale of 1 to 10 with 10 being all the time and 1 being almost never, how much of the time have you felt like you were able to handle all that you had to do?
NeedsBeingMet	not yet	In thinking about the last 7 days, on a scale of 1 to 10 with 10 being all the time and 1 being almost never, how much of the time have you felt like your needs were being met?
OverallStressLevel	not yet	In thinking about the last 7 days, on a scale of 1 to 10 with 10 being the highest: how would you rate your overall stress level?
SatisfactionSleep	not yet	In thinking about these last 7 days, which of these best describes how you felt about your sleep?
ComparisonHoursWorkedToDesired	not yet	How does how does your number of hours worked compare to the number of hours you would like to work?
DiastolicBloodPressure	not yet	What is your Diastolic blood pressure?
ConditionsManagedByDoctor	not yet	How many of your major medical conditions do you regularly see a doctor for status or treatment?
NumberMedications	not yet	How many medications do you take on a regular basis, like every day or every week  These include prescription medications such as pain medicines, and medications that help you manage any chronic conditions?
TimesMeetingSpeakingNonCloseFriends	not yet	Overall during the last month, how many times have you interacted with people in your community outside of your close friends and family, such as an extended conversation with someone at the park, or participated in an event or activity?
OptimisticAboutFuture	not yet	In thinking about the last 7 days, on a scale of 1 to 10 with 10 being all the time and 1 being almost never, how much of the time have you felt optimistic about your future?
GoodAboutLife	not yet	In thinking about the last 7 days, on a scale of 1 to 10 with 10 being all the time and 1 being almost never, how much of the time did you feel good about the way you are living your life?
OverallAnxietyLevel	not yet	In thinking about the last 7 days, on a scale of 1 to 10 with 10 being the highest: how would you rate your overall anxiety level?
OverallHappiness	not yet	In thinking about the last 7 days, on a scale of 1 to 10 with 10 being the highest: how would you rate your overall happiness?
OverallLifeSatisfaction	not yet	In thinking about the last 7 days, on a scale of 1 to 10 with 10 being the highest: how would you rate your overall sense of satisfaction with your life?
MeaningfulRelationships	not yet	In thinking about the last 7 days, on a scale of 1 to 10 with 10 being all the time and 1 being almost never,  how much of the time have you felt like you have meaningful relationships with people in your life?
PainInterferedWithActivities	not yet	Over the last 7 days, on a scale of 1 to 10, with 10 being the most problematic, to what degree has pain of any kind interfered with your day-to-day activities?
OtherFactorsInterferedWithActivities	not yet	Over the last 7 days, on a scale of 1 to 10, with 10 being the most problematic, to what degree did physical, mental, or emotional health factors interfere with your ability to be as actively engaged as you would like?
ReliedOnOthersForHelp	not yet	Over the last 7 days, on a scale of 1 to 10, with 10 being the most help, how much have you relied on another person for day-to-day activities because of any physical, mental, or emotional conditions? (For example, bathing, dressing, walking, going up and down stairs, cooking, shopping, managing your medications, doing your laundry, driving, taking care of your finances?)
\.


--
-- Name: user user_email_key; Type: CONSTRAINT; Schema: vi; Owner: vi
--

ALTER TABLE ONLY vi."user"
    ADD CONSTRAINT user_email_key UNIQUE (email);



--
-- Name: idx_answer__question; Type: INDEX; Schema: vi; Owner: vi
--

CREATE INDEX idx_answer__question ON vi.answer USING btree (question);


--
-- Name: idx_answer__user_question_time_received; Type: INDEX; Schema: vi; Owner: vi
--

CREATE INDEX idx_answer__user_question_time_received ON vi.answer USING btree ("user", question, time_received);


--
-- Name: idx_answer_result; Type: INDEX; Schema: vi; Owner: vi
--

CREATE INDEX idx_answer_result ON vi.answer_result USING btree (result);


--
-- Name: idx_indexcomponent__index; Type: INDEX; Schema: vi; Owner: vi
--

CREATE INDEX idx_indexcomponent__index ON vi.indexcomponent USING btree (index);


--
-- Name: idx_indexsubcomponent__index_component; Type: INDEX; Schema: vi; Owner: vi
--

CREATE INDEX idx_indexsubcomponent__index_component ON vi.indexsubcomponent USING btree (index_component);


--
-- Name: idx_indexsubcomponent_question; Type: INDEX; Schema: vi; Owner: vi
--

CREATE INDEX idx_indexsubcomponent_question ON vi.indexsubcomponent_question USING btree (question);


--
-- Name: idx_result__index; Type: INDEX; Schema: vi; Owner: vi
--

CREATE INDEX idx_result__index ON vi.result USING btree (index);


--
-- Name: idx_result__user_index_time_generated; Type: INDEX; Schema: vi; Owner: vi
--

CREATE INDEX idx_result__user_index_time_generated ON vi.result USING btree ("user", index, time_generated);


--
-- Name: idx_resultcomponent__index_component; Type: INDEX; Schema: vi; Owner: vi
--

CREATE INDEX idx_resultcomponent__index_component ON vi.resultcomponent USING btree (index_component);


--
-- Name: idx_resultcomponent__result; Type: INDEX; Schema: vi; Owner: vi
--

CREATE INDEX idx_resultcomponent__result ON vi.resultcomponent USING btree (result);


--
-- Name: idx_resultsubcomponent__index_sub_component; Type: INDEX; Schema: vi; Owner: vi
--

CREATE INDEX idx_resultsubcomponent__index_sub_component ON vi.resultsubcomponent USING btree (index_sub_component);


--
-- Name: idx_resultsubcomponent__result_component; Type: INDEX; Schema: vi; Owner: vi
--

CREATE INDEX idx_resultsubcomponent__result_component ON vi.resultsubcomponent USING btree (result_component);


--
-- Name: idx_token__jti; Type: INDEX; Schema: vi; Owner: vi
--

CREATE INDEX idx_token__jti ON vi.token USING btree (jti);


--
-- Name: idx_token__user; Type: INDEX; Schema: vi; Owner: vi
--

CREATE INDEX idx_token__user ON vi.token USING btree ("user");


--
-- Name: idx_user__birth_date; Type: INDEX; Schema: vi; Owner: vi
--

CREATE INDEX idx_user__birth_date ON vi."user" USING btree (birth_date);


--
-- Name: idx_user__email_pword; Type: INDEX; Schema: vi; Owner: vi
--

CREATE INDEX idx_user__email_pword ON vi."user" USING btree (email, pword);


--
-- Name: idx_user__gender; Type: INDEX; Schema: vi; Owner: vi
--

CREATE INDEX idx_user__gender ON vi."user" USING btree (gender);

CREATE INDEX idx_user__last_login ON vi."user" USING btree (last_login);

CREATE INDEX idx_user__last_notification ON vi."user" USING btree (last_notification);


--
-- Name: answer fk_answer__question; Type: FK CONSTRAINT; Schema: vi; Owner: vi
--

ALTER TABLE ONLY vi.answer
    ADD CONSTRAINT fk_answer__question FOREIGN KEY (question) REFERENCES vi.question(name);


--
-- Name: answer fk_answer__user; Type: FK CONSTRAINT; Schema: vi; Owner: vi
--

ALTER TABLE ONLY vi.answer
    ADD CONSTRAINT fk_answer__user FOREIGN KEY ("user") REFERENCES vi."user"(id);


--
-- Name: answer_result fk_answer_result__answer; Type: FK CONSTRAINT; Schema: vi; Owner: vi
--

ALTER TABLE ONLY vi.answer_result
    ADD CONSTRAINT fk_answer_result__answer FOREIGN KEY (answer) REFERENCES vi.answer(id);


--
-- Name: answer_result fk_answer_result__result; Type: FK CONSTRAINT; Schema: vi; Owner: vi
--

ALTER TABLE ONLY vi.answer_result
    ADD CONSTRAINT fk_answer_result__result FOREIGN KEY (result) REFERENCES vi.result(id);


--
-- Name: indexcomponent fk_indexcomponent__index; Type: FK CONSTRAINT; Schema: vi; Owner: vi
--

ALTER TABLE ONLY vi.indexcomponent
    ADD CONSTRAINT fk_indexcomponent__index FOREIGN KEY (index) REFERENCES vi.index(name);


--
-- Name: indexsubcomponent fk_indexsubcomponent__index_component; Type: FK CONSTRAINT; Schema: vi; Owner: vi
--

ALTER TABLE ONLY vi.indexsubcomponent
    ADD CONSTRAINT fk_indexsubcomponent__index_component FOREIGN KEY (index_component) REFERENCES vi.indexcomponent(name);


--
-- Name: indexsubcomponent_question fk_indexsubcomponent_question__indexsubcomponent; Type: FK CONSTRAINT; Schema: vi; Owner: vi
--

ALTER TABLE ONLY vi.indexsubcomponent_question
    ADD CONSTRAINT fk_indexsubcomponent_question__indexsubcomponent FOREIGN KEY (indexsubcomponent) REFERENCES vi.indexsubcomponent(name);


--
-- Name: indexsubcomponent_question fk_indexsubcomponent_question__question; Type: FK CONSTRAINT; Schema: vi; Owner: vi
--

ALTER TABLE ONLY vi.indexsubcomponent_question
    ADD CONSTRAINT fk_indexsubcomponent_question__question FOREIGN KEY (question) REFERENCES vi.question(name);


--
-- Name: result fk_result__index; Type: FK CONSTRAINT; Schema: vi; Owner: vi
--

ALTER TABLE ONLY vi.result
    ADD CONSTRAINT fk_result__index FOREIGN KEY (index) REFERENCES vi.index(name);


--
-- Name: result fk_result__user; Type: FK CONSTRAINT; Schema: vi; Owner: vi
--

ALTER TABLE ONLY vi.result
    ADD CONSTRAINT fk_result__user FOREIGN KEY ("user") REFERENCES vi."user"(id);


--
-- Name: resultcomponent fk_resultcomponent__index_component; Type: FK CONSTRAINT; Schema: vi; Owner: vi
--

ALTER TABLE ONLY vi.resultcomponent
    ADD CONSTRAINT fk_resultcomponent__index_component FOREIGN KEY (index_component) REFERENCES vi.indexcomponent(name);


--
-- Name: resultcomponent fk_resultcomponent__result; Type: FK CONSTRAINT; Schema: vi; Owner: vi
--

ALTER TABLE ONLY vi.resultcomponent
    ADD CONSTRAINT fk_resultcomponent__result FOREIGN KEY (result) REFERENCES vi.result(id);


--
-- Name: resultsubcomponent fk_resultsubcomponent__index_sub_component; Type: FK CONSTRAINT; Schema: vi; Owner: vi
--

ALTER TABLE ONLY vi.resultsubcomponent
    ADD CONSTRAINT fk_resultsubcomponent__index_sub_component FOREIGN KEY (index_sub_component) REFERENCES vi.indexsubcomponent(name);


--
-- Name: resultsubcomponent fk_resultsubcomponent__result_component; Type: FK CONSTRAINT; Schema: vi; Owner: vi
--

ALTER TABLE ONLY vi.resultsubcomponent
    ADD CONSTRAINT fk_resultsubcomponent__result_component FOREIGN KEY (result_component) REFERENCES vi.resultcomponent(id);


--
-- Name: token fk_token__user; Type: FK CONSTRAINT; Schema: vi; Owner: vi
--

ALTER TABLE ONLY vi.token
    ADD CONSTRAINT fk_token__user FOREIGN KEY ("user") REFERENCES vi."user"(id);


