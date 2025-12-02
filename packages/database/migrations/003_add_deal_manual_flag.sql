-- Migration: Add manual qualification flag to deals
-- This prevents the bot from overwriting manual CRM changes

-- Add manually_qualified column
ALTER TABLE public.deals 
ADD COLUMN manually_qualified BOOLEAN DEFAULT FALSE NOT NULL;

-- Add index for filtering
CREATE INDEX idx_deals_manually_qualified ON public.deals(manually_qualified);

-- Add comment for documentation
COMMENT ON COLUMN public.deals.manually_qualified IS 
'True if deal stage was manually edited from CRM, preventing bot auto-updates';

-- Update existing deals to be marked as not manually qualified
UPDATE public.deals SET manually_qualified = FALSE WHERE manually_qualified IS NULL;
