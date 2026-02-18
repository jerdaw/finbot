"""Disclaimer display utilities for the Finbot dashboard."""

from __future__ import annotations

import streamlit as st


def show_sidebar_disclaimer() -> None:
    """Display a concise disclaimer in the sidebar.

    This should be called at the top of every dashboard page to ensure
    users see the disclaimer regardless of which page they visit.
    """
    with st.sidebar:
        st.warning("⚠️ **DISCLAIMER**")
        st.markdown(
            """
            **For Educational Purposes Only**

            This software does NOT provide financial, investment, or medical advice.

            - Past performance does NOT predict future results
            - You may lose money
            - NO warranty or guarantee
            - Consult qualified professionals

            [**Read Full Disclaimer**](https://github.com/jerdaw/finbot/blob/main/DISCLAIMER.md)
            """,
            unsafe_allow_html=False,
        )
        st.markdown("---")


def show_sidebar_accessibility() -> None:
    """Display accessibility information in the sidebar.

    Provides quick access to accessibility features and documentation.
    """
    with st.sidebar, st.expander("♿ **Accessibility**"):
        st.markdown(
            """
                **WCAG 2.1 Level AA (Partial)**

                **Features:**
                - ✓ High contrast colors
                - ✓ Colorblind-friendly palettes
                - ✓ Keyboard navigation
                - ✓ Screen reader support

                **Keyboard Shortcuts:**
                - Tab: Navigate elements
                - Enter/Space: Activate
                - Esc: Close dropdowns

                [**Accessibility Docs**](https://github.com/jerdaw/finbot/blob/main/docs/accessibility.md)

                [**Report Issues**](https://github.com/jerdaw/finbot/issues)
                """,
            unsafe_allow_html=False,
        )


def show_full_disclaimer_section() -> None:
    """Display the full disclaimer section on the home page.

    This provides more detailed information than the sidebar version.
    Only use this on the main dashboard page, not on every page.
    """
    st.markdown("---")
    st.markdown("## IMPORTANT DISCLAIMER")
    st.error(
        """
        **⚠️ Educational and Research Purposes Only**

        Finbot is NOT financial advice. This software is provided for educational and research purposes only.

        - **NOT FINANCIAL ADVICE**: Do not use as a substitute for professional financial advisors
        - **PAST PERFORMANCE**: Historical results do not guarantee future returns. You may lose money.
        - **NO WARRANTY**: Provided "AS IS" without warranty. Results may contain errors.
        - **CONSULT PROFESSIONALS**: Always consult qualified financial advisors, tax professionals,
          and healthcare providers
        - **YOUR RISK**: You are solely responsible for your decisions and any losses

        **By using this software, you accept all risks and acknowledge all limitations.**

        📄 [Read the complete disclaimer](https://github.com/jerdaw/finbot/blob/main/DISCLAIMER.md)
        for full legal terms and risk disclosures.
        """
    )
