interface CredentialResponse {
    credential: string;
    select_by: string;
}

interface GsiButtonConfiguration {
    type?: 'standard' | 'icon';
    theme?: 'outline' | 'filled_blue' | 'filled_black';
    size?: 'large' | 'medium' | 'small';
    text?: string;
    shape?: 'rectangular' | 'pill' | 'circle' | 'square';
    logo_alignment?: 'left' | 'center';
    width?: number;
    locale?: string;
}

interface Window {
    google: {
        accounts: {
            id: {
                initialize: (config: {
                    client_id: string;
                    callback: (response: CredentialResponse) => void;
                }) => void;
                renderButton: (
                    element: HTMLElement,
                    config: GsiButtonConfiguration
                ) => void;
                prompt: () => void;
            };
        };
    };
}
