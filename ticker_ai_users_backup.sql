--
-- PostgreSQL database dump
--

-- Dumped from database version 16.9
-- Dumped by pg_dump version 16.5

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: users; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.users (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    email character varying(255) NOT NULL,
    phone character varying(50),
    password_hash character varying(255) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.users OWNER TO neondb_owner;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO neondb_owner;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.users (id, name, email, phone, password_hash, created_at) FROM stdin;
1	Grant Kraemer	gkraem@vt.edu	2402857119	$pbkdf2-sha256$29000$m1PKOUfoPQdAaM25N2ZsDQ$L3noPkGbFnjinh4.10srgx2haCLbv4eSBcV.DHooqFI	2025-05-10 14:25:40.754942
3	Jodi Mientkiewicz	jodo525@aol.com	3057263795	temp_password_hash	2025-05-27 16:32:38.985658
4	Lawrence Kraemer	lkraeg@yahoo.com	3016744843	temp_password_hash	2025-05-27 16:11:04.854791
5	Jennifer kraemer 	j.kraemer@yahoo.com	7039193451	$pbkdf2-sha256$29000$NkZozRlDqFUqBSCEUAqBUA$u0VT1e2qIshA3Z/E/G4fJtJBY4kKw47qNAzxriJn03Y	2025-05-27 19:52:30.146201
6	Josh Sapirstein	jsapirsteindev@gmail.com	3399333381	$pbkdf2-sha256$29000$VEophXCOUYqxFmLMmRNCiA$NhjH6Oz23HaVhpPLeu735fxbCmL3ulC6tmAOIDSWT4w	2025-05-27 19:56:36.834782
7	Lawrence  Kraemer 	lkeagle@yahoo.com	3016744843	$pbkdf2-sha256$29000$AWCsdc45hxAC4Lx3jpESwg$k3.rwJIWyoSivIK1h00weOdDSvUjuQ6eCCZXuqlvmaU	2025-05-28 01:38:09.988366
\.


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.users_id_seq', 7, true);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: public; Owner: cloud_admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE cloud_admin IN SCHEMA public GRANT ALL ON SEQUENCES TO neon_superuser WITH GRANT OPTION;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: cloud_admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE cloud_admin IN SCHEMA public GRANT ALL ON TABLES TO neon_superuser WITH GRANT OPTION;


--
-- PostgreSQL database dump complete
--

