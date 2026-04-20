import { PublicWidgetFrame } from '@/components/widget/PublicWidgetFrame';

type SearchParams = Promise<Record<string, string | string[] | undefined>>;

function getFirstValue(value: string | string[] | undefined, fallback = ''): string {
    if (Array.isArray(value)) {
        return value[0] || fallback;
    }
    return value || fallback;
}

export default async function WidgetPage({ searchParams }: { searchParams: SearchParams }) {
    const params = await searchParams;
    return (
        <PublicWidgetFrame
            widgetId={getFirstValue(params.widgetId)}
            primaryColor={getFirstValue(params.primaryColor, '#7C3AED')}
            apiBase={getFirstValue(params.apiBase, process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '')}
            hostPageUrl={getFirstValue(params.pageUrl)}
        />
    );
}
