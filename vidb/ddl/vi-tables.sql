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


