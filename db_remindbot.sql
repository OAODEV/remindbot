CREATE DATABASE remindbot OWNER remindbot;

\c remindbot

CREATE TABLE reminder (
    reminder_id serial primary key,
    reminder_task text,
    trigger_dt timestamp with time zone,
    channel_code character varying(21) DEFAULT 'C06PUC895'::character varying,
    channel_name character varying(21) DEFAULT 'xyz-bot-testing'::character varying,
    username character varying(100),
    user_code character varying(20),
    sent_flag boolean DEFAULT false
);