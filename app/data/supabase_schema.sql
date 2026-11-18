-- ==============================================================================
-- SSC CGL MAINS 2026 TEST PORTAL - SUPABASE POSTGRESQL PRODUCTION SCHEMA
-- ==============================================================================
-- Run this script in your Supabase SQL Editor (Dashboard -> SQL Editor -> New Query)
-- It creates all required tables, Row Level Security (RLS) policies, and performance indexes.

-- 1. Profiles Table (Extends Supabase Auth users)
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT DEFAULT 'student' CHECK (role IN ('student', 'admin')),
    target_exam TEXT DEFAULT 'SSC CGL 2026',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Mock Tests Metadata & Content
CREATE TABLE IF NOT EXISTS public.tests (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    subtitle TEXT,
    category TEXT DEFAULT 'Tier-2 Quantitative Aptitude',
    duration_minutes INTEGER DEFAULT 35,
    num_questions INTEGER DEFAULT 25,
    marks_per_question INTEGER DEFAULT 3,
    negative_marks INTEGER DEFAULT 1,
    questions_json JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Multi-Tenant Test Results & Detailed Evaluated Submissions
CREATE TABLE IF NOT EXISTS public.test_results (
    id TEXT PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    user_name TEXT,
    user_email TEXT,
    test_id TEXT NOT NULL,
    test_title TEXT NOT NULL,
    score INTEGER NOT NULL,
    max_marks INTEGER DEFAULT 75,
    accuracy INTEGER DEFAULT 0,
    attempted INTEGER DEFAULT 0,
    correct INTEGER DEFAULT 0,
    incorrect INTEGER DEFAULT 0,
    unattempted INTEGER DEFAULT 0,
    time_spent_seconds INTEGER DEFAULT 0,
    questions_evaluated_json JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Student Personal Study Notes
CREATE TABLE IF NOT EXISTS public.student_notes (
    id TEXT PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    topic TEXT DEFAULT 'General',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Study Materials & Syllabi
CREATE TABLE IF NOT EXISTS public.study_materials (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    content_markdown TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for lightning fast queries
CREATE INDEX IF NOT EXISTS idx_results_user_id ON public.test_results(user_id);
CREATE INDEX IF NOT EXISTS idx_results_created_at ON public.test_results(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_notes_user_id ON public.student_notes(user_id);

-- ==============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- Ensures each student can ONLY see and modify their OWN test results and notes!
-- ==============================================================================

ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.test_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.student_notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.study_materials ENABLE ROW LEVEL SECURITY;

-- Profiles Policies
CREATE POLICY "Public profiles are viewable by authenticated users" 
ON public.profiles FOR SELECT TO authenticated USING (true);

CREATE POLICY "Users can insert their own profile" 
ON public.profiles FOR INSERT WITH CHECK (auth.uid() = id);

CREATE POLICY "Users can update their own profile" 
ON public.profiles FOR UPDATE USING (auth.uid() = id);

-- Tests Policies (Public read for all students)
CREATE POLICY "Tests viewable by all students" 
ON public.tests FOR SELECT TO authenticated, anon USING (true);

CREATE POLICY "Admins can manage tests" 
ON public.tests FOR ALL TO authenticated 
USING (EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin'));

-- Test Results Policies (Strict Student Isolation)
CREATE POLICY "Students can view their own test results" 
ON public.test_results FOR SELECT TO authenticated 
USING (auth.uid() = user_id OR EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin'));

CREATE POLICY "Students can submit their own test results" 
ON public.test_results FOR INSERT TO authenticated 
WITH CHECK (auth.uid() = user_id);

-- Notes Policies (Strict Student Isolation)
CREATE POLICY "Students can view their own notes" 
ON public.student_notes FOR SELECT TO authenticated 
USING (auth.uid() = user_id);

CREATE POLICY "Students can create their own notes" 
ON public.student_notes FOR INSERT TO authenticated 
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Students can update their own notes" 
ON public.student_notes FOR UPDATE TO authenticated 
USING (auth.uid() = user_id);

CREATE POLICY "Students can delete their own notes" 
ON public.student_notes FOR DELETE TO authenticated 
USING (auth.uid() = user_id);

-- Study Materials Policies (Read-only for all students)
CREATE POLICY "Study materials viewable by all students" 
ON public.study_materials FOR SELECT TO authenticated, anon USING (true);

-- Auto-create profile on signup trigger
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, email, full_name, role, target_exam)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'full_name', 'Student'),
    COALESCE(NEW.raw_user_meta_data->>'role', 'student'),
    COALESCE(NEW.raw_user_meta_data->>'target_exam', 'SSC CGL 2026')
  )
  ON CONFLICT (id) DO NOTHING;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();
